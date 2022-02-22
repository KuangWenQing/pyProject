from simulator.SIM_Raw import get_epoch_raw_from_simulator
import threading
import os, sys
import logging
logging.basicConfig(level=logging.INFO, format='%(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

GPS_SYS = 0
BDS_SYS = 3

total_bits = 0
error_bits = 0
semaphore = threading.Semaphore(0)
condition = threading.Condition()
g_dd = {}
g_sow = 0
stop_run = False


def raw_str_to_origin_raw(s: str):
    """
    和芯星通 B1C电文 去掉 结尾 16 bits
    再 去掉 高2位 补的 1 (或者叫 保留 878 bit)
    """
    return (int(s, 16) >> 16) & ~(0x3 << 878)


def get_sow_from_origin_raw(raw_int: int):
    """获取周内秒 从 原始电文"""
    # SOH 在 高 7 ~ 14bit , 缩放因子 为 18
    seconde_of_hour = ((raw_int >> 864) & 0xff) * 18

    # HOW 在 28 ~ 35 bit ， 缩放因子 为 1
    hour_of_week = (raw_int >> 843) & 0xff

    return hour_of_week * 3600 + seconde_of_hour


def hxxt_process(path_file):
    global g_dd, g_sow, error_bits, total_bits, stop_run
    condition.acquire()  # 尝试获得锁， 没有获得就阻塞在此
    print('HXXT_process start')
    semaphore.release()  # 释放 信号量
    with open(path_file) as fd:
        for row in fd:
            if not row.startswith("#RAWBD3SUBFRAMEA"):
                continue
            _, info_str = row.split(";")
            info_str, _crc_ = info_str.split("*")
            info = info_str.split(',')

            sv_id = info[1]
            raw_str = info[4]
            origin_raw_int = raw_str_to_origin_raw(raw_str)
            sow = get_sow_from_origin_raw(origin_raw_int)

            while sow > g_sow:
                condition.acquire()
                # semaphore.release()  # 释放信号量
                logging.debug("sow = {}".format(sow))
                condition.notify()  # 提醒其它线程有锁将要释放
                condition.wait()
                if stop_run:
                    break
                condition.release()  # 释放锁
            if sow < g_sow:
                continue
            else:
                assert sv_id in g_dd.keys()
                sim_raw_int = int(g_dd[sv_id][1], 16) >> 2
                # 模拟器将第一个字设为全0， 第一个字占 14 bit
                if (origin_raw_int & ~(0x3fff << 864)) != (sim_raw_int & ~(0x3fff << 864)):
                    sim_raw_str = "{:0878b}".format(sim_raw_int)
                    origin_raw_str = "{:0878b}".format(origin_raw_int)
                    # 第一个字不用对比， 第二个字的 校验位(最后24bit)不用对比
                    for i in range(14, 590):
                        if sim_raw_str[i] != origin_raw_str[i]:
                            error_bits += 1
                        else:
                            total_bits += 1
                    # 第3个字的 校验位(最后24bit)不用对比
                    for i in range(614, 864):
                        if sim_raw_str[i] != origin_raw_str[i]:
                            error_bits += 1
                        else:
                            total_bits += 1
                else:
                    total_bits += 816
            if stop_run:
                break
    stop_run = True


def simulate_process(path_file: str, begin_time=518400000):
    global g_dd, g_sow, stop_run
    if not os.path.exists(path_file):
        print("No such file :: ", path_file)
        sys.exit(-1)
    semaphore.acquire()  # 等待获取信号量
    fd = open(path_file, 'r')
    print('simulate_process start')
    condition.acquire()  # 尝试获得锁， 没有获得就阻塞在此
    for dd in get_epoch_raw_from_simulator(fd, begin_time, BDS_SYS):
        # semaphore.acquire()  # 等待获取信号量
        condition.acquire()  # 尝试获得锁， 没有获得就阻塞在此
        if stop_run:
            break
        key_list = list(dd.keys())
        g_sow = dd[key_list[0]][0]
        g_dd = dd
        logging.debug("g_sow = {}".format(g_sow))
        condition.notify()  # 提醒其它线程有锁将要释放
        condition.wait()
        condition.release()  # 释放锁
    fd.close()
    stop_run = True
    condition.notify()   # 提醒其它线程有锁将要释放
    condition.release()  # 释放 信号量


if __name__ == "__main__":
    path = r"D:\work\temp\1118" + "\\"
    sim_file = r"D:\work\temp\simulate\user_fix.rsim_(M3B1-BD2_B1C2)_RawNav(20211113-1106).dat.TXT"
    hxxt_file = "2_b1c_raw_power30dB.log"

    sim = threading.Thread(target=simulate_process, args=(sim_file, 86418000))
    hxxt = threading.Thread(target=hxxt_process, args=(path + hxxt_file, ))
    sim.start()
    hxxt.start()
    sim.join()
    hxxt.join()
    print("error_bits = {}, total_bits = {}, symbol error rate = {:.2%}".
          format(error_bits, total_bits, error_bits / total_bits))
