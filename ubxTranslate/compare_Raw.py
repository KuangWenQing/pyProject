from simulator.SIM_Raw import get_epoch_raw_from_simulator
from ubxTranslate.UBX_RXM import get_raw_word_from_ubx
from threading import Thread, Event, Condition, Semaphore
import time
import sys, os
import logging

logging.basicConfig(level=logging.INFO, format='%(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

import subprocess, re
from multiprocessing import Pool, Value, Manager, Process


def process_info():
    pid = os.getpid()
    res = subprocess.getstatusoutput('ps aux|grep '+str(pid))[1].split('\n')[0]

    p = re.compile(r'\s+')
    l = p.split(res)
    info = {'user':l[0],
        'pid':l[1],
        'cpu':l[2],
        'mem':l[3],
        'vsa':l[4],
        'rss':l[5],
        'start_time':l[6]}
    print(info)


def which_cpu():
    pid = os.getpid()
    # res = subprocess.getstatusoutput('taskset -cp '+str(pid))  #[1].split('list:')[1]
    res = subprocess.getstatusoutput('ps -o psr -p ' + str(pid))[1].split('\n')[1]
    # print("process", str(pid), "on cpu", res)
    return "pid = " + str(pid) + "  on CPU" + res


g_sow = 0
g_dd = {}
sv_id = -1
words = []

stop_run = 0

total_bits = 0
error_bits = 0

event = Event()
'''
event 对象最好单次使用，就是说，你创建一个 event 对象，让某个线程等待这个
对象，一旦这个对象被设置为真，你就应该丢弃它。尽管可以通过 clear() 方法来重
置 event 对象，但是很难确保安全地清理 event 对象并对它重新赋值。很可能会发生错
过事件、死锁或者其他问题（特别是，你无法保证重置 event 对象的代码会在线程再次
等待这个 event 对象之前执行）。如果一个线程需要不停地重复使用 event 对象，你最
好使用 Condition 对象来代替。'''
condition = Condition()
semaphore = Semaphore(0)


# pool = Pool(processes=4)
err_bits = Value('i', 0)
tot_bits = Value('i', 0)
manager = Manager()
q = manager.Queue(maxsize=1)
lock = manager.Lock()   # 初始化一把锁


def simulate_thread(path_file: str):
    global g_dd, g_sow, stop_run
    if not os.path.exists(path_file):
        sys.exit(-1)
    fd = open(path_file, 'r')
    event.wait()
    print('simulate_thread start')
    for dd in get_epoch_raw_from_simulator(fd):
        condition.acquire()
        key_list = list(dd.keys())
        g_sow = dd[key_list[0]][1] >> 13
        g_dd = dd
        logging.debug("g_sow = {}".format(g_sow))
        # semaphore.release()  # 释放 信号量
        condition.notify()
        if stop_run:
            break
        condition.wait()
        condition.release()
    print('simulate_thread end')


def ubx_thread(path_file: str):
    global sv_id, words, stop_run, total_bits, error_bits
    print('ubx_thread start')
    event.set()
    for prn_words in get_raw_word_from_ubx(path_file):
        sv_id, words = prn_words
        if words:
            sow = (words[1] & 0x3fffffff) >> 13
            condition.acquire()
            while sow > g_sow:
                logging.debug("sow = {}".format(sow))

                condition.notify()
                condition.wait()
                # semaphore.acquire()  # 等待获取信号量
            condition.release()

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
                        total_bits += 24                        # 24个位都正确
        else:
            condition.acquire()
            stop_run = True
            print('ubx_thread end')
            condition.notify()
            condition.release()
            return


def simulate_process(path_file: str, ):
    global q, lock
    if not os.path.exists(path_file):
        sys.exit(-1)
    fd = open(path_file, 'r')

    print('simulate_process start. ', which_cpu())
    # process_info()
    # which_cpu()

    for dd in get_epoch_raw_from_simulator(fd):
        q.put(dd)

        lock.acquire()
        key_list = list(dd.keys())
        second_of_week = dd[key_list[0]][1] >> 13
        lock.release()
        logging.debug("simulate_sow = {}".format(second_of_week))

    ubx.terminate()
    print('simulate_process end')


def ubx_process(path_file: str,):
    global q, err_bits, tot_bits
    sim_sow, sow = 0, 0
    sim_dd = {}
    print('ubx_process start. ', which_cpu())
    # process_info()
    # which_cpu()

    for prn_words in get_raw_word_from_ubx(path_file):
        sv_id, words = prn_words
        if words:
            sow = (words[1] & 0x3fffffff) >> 13
            logging.debug("sow = {}".format(sow))

            while sim_sow < sow:
                sim_dd = q.get()
                sim_sow = sim_dd[str(sv_id)][1] >> 13

            if sim_sow > sow:
                continue

            sim_sv_raw = sim_dd[str(sv_id)]
            for i in range(10):
                if (sim_sv_raw[i] >> 6) != (words[i] & 0x3fffffff) >> 6:    # ubx 高2位 补了 1， 凑齐了 32 个 bit
                    sim_raw_bin_str = bin(sim_sv_raw[i] | 0xc0000000)[4:]   # 高2位补1, 保证高位为0时不被清理掉，去掉0b11
                    ubx_raw_bin_str = bin(words[i])[4:]     # 去掉 0b11
                    for idx in range(24):                   # 每个字只比较 高 24 位 ， 最后 6 位 是奇偶校验
                        # try:
                        if sim_raw_bin_str[idx] != ubx_raw_bin_str[idx]:
                            err_bits.value += 1
                        else:
                            tot_bits.value += 1
                        # except:
                        #     print('sss')
                else:
                    tot_bits.value += 24                        # 24个位都正确
        else:
            sim.terminate()
            print('ubx_process end')
            return


if __name__ == '__main__':
    path = r"/home/ucchip/tmp/1208" + "/"
    ubx_file = "COM3_211028_042604_M8T.ubx"
    simulator_file = r"中央公园广场.RSIM_(M1B1-GPS_L1)_RawNav(20211028-1225).dat.TXT"
    time_start = time.time()

    # sim = Thread(target=simulate_thread, args=(path + simulator_file, ))
    # ubx = Thread(target=ubx_thread, args=(path + ubx_file, ))

    sim = Process(target=simulate_process, args=(path + simulator_file,))
    ubx = Process(target=ubx_process, args=(path + ubx_file,))
    sim.start()
    ubx.start()
    sim.join()
    ubx.join()

    total_bits = tot_bits.value
    error_bits = err_bits.value
    print("error_bits = {:d}, total_bits = {:d}, symbol error rate = {:.2%}".format(error_bits, total_bits, error_bits / total_bits))
    print("used time = {:.3f}s".format(time.time() - time_start))
