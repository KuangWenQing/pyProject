#!/usr/bin/env python

import re
import os
import sys
import time
import numpy as np
from simulator.SIM_Raw import get_epoch_raw_from_simulator
from threading import Thread, Condition, Semaphore
condition = Condition()
semaphore = Semaphore(0)


def simulate_process(path_file: str, begin_time=86400):
    global g_dd, g_sow, stop_run, condition, semaphore
    if not os.path.exists(path_file):
        sys.exit(-1)
    fd = open(path_file, 'r')
    semaphore.acquire()  # 等待获取信号量
    # print('simulate_process star')
    for dd in get_epoch_raw_from_simulator(fd, begin_time):
        semaphore.acquire()  # 等待获取信号量
        condition.acquire()  # 尝试获得锁， 没有获得就阻塞在此
        if stop_run:
            break
        key_list = list(dd.keys())
        g_sow = (dd[key_list[0]][1] >> 13) * 6
        g_dd = dd
        condition.notify()      # 提醒其它线程有锁将要释放
        condition.release()     # 释放锁
    fd.close()
    condition.notify()  # 提醒其它线程有锁将要释放
    condition.release()  # 释放锁


def uc8088_process(path_file: str):
    global err_total, crc_total, condition, semaphore, stop_run
    row_cnt = 0
    chl_time = -1
    compare_flag = False
    crc_row_mark = re.compile(r'sv\d+ crc:')
    chl_time_mark = "CHL TIME"
    condition.acquire()  # 尝试获得锁， 没有获得就阻塞在此
    # print("uc8088_process running!")
    semaphore.release()  # 释放 信号量
    with open(path_file, 'r') as fd:
        for row in fd:
            row_cnt += 1
            if crc_row_mark.match(row) and compare_flag:
                sv_id = str(int(row[2:4]) + 1)
                crc_row_lst = row[row.index(':')+1:].split()
                word_lst = [int(item, 16) & 0x3fffffff for item in crc_row_lst]
                temp_ = err_total
                for i in range(10):
                    crc_total += 24  # 一个字共有30 个bit ，数据位占24 bit，校验位占6bit
                    if word_lst[i] & ~0x3f != g_dd[sv_id][i] & ~0x3f:
                        uc_word_bit_str = "{:030b}".format(word_lst[i])
                        sim_word_bit_str = "{:030b}".format(g_dd[sv_id][i])
                        # print("word {:d}  uc = {:s}   sim = {:s}".format(i, uc_word_bit_str, sim_word_bit_str))
                        for idx in range(24):
                            if uc_word_bit_str[idx] != sim_word_bit_str[idx]:
                                err_total += 1
                if err_total > temp_:
                    # print("the %d line error %d bits" % (row_cnt, err_total - temp_))
                    # print(row)
                    continue
            elif row.startswith(chl_time_mark):
                chl_time_row_lst = row.split(',')
                chl_time = round(int(chl_time_row_lst[1]) / 1000)

            if chl_time > g_sow:
                semaphore.release()  # 释放 信号量
                compare_flag = False
                condition.wait()
            elif chl_time < g_sow:
                compare_flag = False
            else:
                compare_flag = True

    semaphore.release()  # 释放 信号量
    condition.notify()  # 提醒其它线程有锁将要释放
    condition.release()  # 释放锁
    stop_run = 1


if __name__ == "__main__":
    path = r"D:\work\lab_test\gnss_acq_parameter_test\1111" + "\\"
    file_8088_lst = [f for f in os.listdir(path) if f.endswith("log")]
    # file_8088_lst = ["2_mdl_new8_acqThre_nct20coh9_-144_gps_dopp10_10_0_0_para83_69_42_22_0_22_12_1_10_32_1163918_rxsc0_SLVL3.log",]
    dir_sim_file = r"D:\work\lab_test\gnss_acq_parameter_test\fix_pr_1e7.RSIM_(M1B1-GPS_L1)_RawNav(20211116-1959).dat.TXT"
    for file in file_8088_lst:
        g_dd, g_sow = {}, 0
        err_total, crc_total, stop_run = 0, 0, 0
        sim = Thread(target=simulate_process, args=(dir_sim_file, 518400))
        ubx = Thread(target=uc8088_process, args=(path + file,))
        sim.start()
        ubx.start()

        sim.join()
        ubx.join()

        print(file)
        print("err_total = {:d}  crc_total = {:d}  error rate = {:.3%} \n".format(err_total, crc_total, err_total/crc_total))

