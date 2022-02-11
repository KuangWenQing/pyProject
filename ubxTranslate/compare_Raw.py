from simulator.SIM_Raw import get_epoch_raw_from_simulator
from UBX_RXM import get_raw_word_from_ubx
from threading import Thread, Event, Semaphore
import time
import sys, os

g_sow = 0
g_dd = {}
sv_id = -1
words = []

stop_run = False

total_bits = 0
error_bits = 0

event = Event()
semaphore = Semaphore(0)


def simulate_process(path_file: str):
    global g_dd, g_sow, stop_run
    if not os.path.exists(path_file):
        sys.exit(-1)
    fd = open(path_file, 'r')
    print('simulate_process star')
    for dd in get_epoch_raw_from_simulator(fd):
        event.wait()  # 等待事件
        if stop_run:
            sys.exit()
        key_list = list(dd.keys())
        g_sow = dd[key_list[0]][1] >> 13
        g_dd = dd
        semaphore.release()  # 释放 信号量


def ubx_process(path_file: str):
    global sv_id, words, stop_run, total_bits, error_bits
    print('ubx_process star')
    for prn_words in get_raw_word_from_ubx(path_file):
        sv_id, words = prn_words
        if words:
            sow = (words[1] & 0x3fffffff) >> 13
            while sow > g_sow:
                event.set()
                semaphore.acquire()  # 等待获取信号量
                event.clear()

            if sow < g_sow:
                continue
            else:
                sim_sv_raw = g_dd[str(sv_id)]
                for i in range(10):
                    if (sim_sv_raw[i] >> 6) != (words[i] & 0x3fffffff) >> 6:    # ubx 高2位 补了 1， 凑齐了 32 个 bit
                        sim_raw_bin_str = bin(sim_sv_raw[i] | 0xc0000000)[4:]   # 高2位补1, 保证高位为0时不被清理掉，去掉0b11
                        ubx_raw_bin_str = bin(words[i])[4:]     # 去掉 0b11
                        for idx in range(24):                   # 每个字只比较 高 24 位 ， 最后 6 位 是奇偶校验
                            if sim_raw_bin_str[idx] != ubx_raw_bin_str[idx]:
                                error_bits += 1
                            else:
                                total_bits += 1
                    else:
                        total_bits += 24
        else:
            stop_run = True
            event.set()
            return None


if __name__ == '__main__':
    path = r"/home/kwq/tmp/kwq/"
    ubx_file = "COM3_211028_042604_M8T.ubx"
    simulator_file = r"中央公园广场.RSIM_(M1B1-GPS_L1)_RawNav(20211028-1225).dat.TXT"

    time_start = time.time()
    sim = Thread(target=simulate_process, args=(path + simulator_file, ))
    ubx = Thread(target=ubx_process, args=(path + ubx_file, ))
    sim.start()
    ubx.start()
    sim.join()
    ubx.join()
    print("error_bits = {}, total_bits = {}, symbol error rate = {:.2%}".format(error_bits, total_bits, error_bits / total_bits))
    print("used time = {:.3f}s".format(time.time() - time_start))
