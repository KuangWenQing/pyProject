"""
use F9P test simulator Signal accuracy
用F9P 测试模拟器 的信号精度
"""

import sys
from collections import deque
from ubxTranslate.UBX_RXM import get_epoch_RAWX_from_ubx
from ubxTranslate.core import Parser
from ubxTranslate.predefined import RXM_CLS
import numpy as np
import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
GPS_SYS = 0


class ChannelUniformityTest:
    def __init__(self, dir_file):
        self.dir_file = dir_file
        try:
            self.fd = open(dir_file, 'rb')
        except:
            print("open ", dir_file, " error")
            sys.exit(-1)

    def channel_uniformity(self):
        """
        通道一致性测试
        """
        pr_diff_list = []
        for d in get_epoch_RAWX_from_ubx(self.fd, GPS_SYS):
            pr_lst = []
            for k in d.keys():
                pr_lst.append(d[k].prMes)
            pr_diff_list.append(max(pr_lst) - min(pr_lst))
        max_pr_diff = max(pr_diff_list)
        mean_pr_diff = np.mean(pr_diff_list)
        print("max diff pr = {:.4f}, time = {:.2f} ns".format(max_pr_diff, max_pr_diff / 0.3))
        print("mean pr diff = {:.4f}, time = {:.2f} ns".format(mean_pr_diff, mean_pr_diff / 0.3))
        print("std pr diff =", round(np.std(pr_diff_list), 4))


def get_all_pr_ca(stream, GNSS_SYS=GPS_SYS) -> list:
    RXM_ID = 0x02
    RAWX_ID = 0x15
    parser = Parser([RXM_CLS])
    ret = []
    while True:
        msg = parser.receive_from(stream, RXM_ID, RAWX_ID)
        if msg:
            ret_dd = {}
            for sv_information in msg[2].RB:
                if sv_information.gnssId == GNSS_SYS:
                    ret_dd[sv_information.svId] = (sv_information.prMes, sv_information.cpMes)
            ret.append(ret_dd)
        elif msg is False:
            return ret


def compare_adjacent(l: list, ca_flag=True):
    """
    return {卫星号： [相邻伪距差]}, {卫星号: [相邻载波（个数）差]}
    """
    length = len(l)
    print("epoch total =", length)
    assert isinstance(l[0], dict)
    delta_pr = {}
    delta_ca = {}
    for key in l[0].keys():
        assert isinstance(l[0][key], tuple)
        delta_ca[key] = []
        delta_pr[key] = []
    for i in range(length - 1):
        epoch_now: dict = l[i]
        epoch_next: dict = l[i + 1]
        for key in epoch_now.keys():
            delta_pr[key].append(epoch_next[key][0] - epoch_now[key][0])
            if ca_flag:
                delta_ca[key].append(epoch_next[key][1] - epoch_now[key][1])
    return delta_pr, delta_ca


def clock_diff(_path_, _file_):
    """计算 ublox 钟差
    """
    fd_ubx = open(_path_ + _file_, 'rb')
    delta_pr, _ = compare_adjacent(get_all_pr_ca(fd_ubx), False)
    assert isinstance(delta_pr, dict)
    all_chl_clock_diff = {}
    for key in delta_pr.keys():
        assert isinstance(delta_pr[key], list)
        all_chl_clock_diff[key] = []
    for key in delta_pr.keys():
        for i in range(len(delta_pr[key]) - 1):
            all_chl_clock_diff[key].append(delta_pr[key][i + 1] - delta_pr[key][i])

    all_chl_clock_diff_mean = []
    for key in all_chl_clock_diff.keys():
        all_chl_clock_diff_mean.append(np.mean(all_chl_clock_diff[key]))

    return np.mean(all_chl_clock_diff_mean)


def diff_delta_pr_delta_ca(delta_pr: dict, delta_ca: dict) -> dict:
    """
    相邻伪距差 - 相邻载波（个数）差 * 波长
    """
    assert isinstance(delta_pr, dict)
    assert isinstance(delta_ca, dict)
    wavelength = 3e8 / 1575420000
    diff_pr_ca = {}
    for key in delta_pr.keys():
        assert len(delta_pr[key]) == len(delta_ca[key])
        diff_pr_ca[key] = []
        for i in range(len(delta_pr[key])):
            diff_pr_ca[key].append(delta_pr[key][i] - wavelength * delta_ca[key][i])
    return diff_pr_ca


def pr_ca_control_accuracy(_path_, _file_):
    """
    载波相位控制精度
    """
    result = {"sv": [], "min": [], "max": [], "median": [],
              "mean": [], "std": [], "cnt": []}
    fd_ubx = open(_path_ + _file_, 'rb')
    ret_pr, ret_ca = compare_adjacent(get_all_pr_ca(fd_ubx))
    dd = diff_delta_pr_delta_ca(ret_pr, ret_ca)
    for key in dd.keys():
        result["sv"].append(key)
        result["min"].append(round(min(dd[key]), 4))
        result["max"].append(round(max(dd[key]), 4))
        result["median"].append(round(np.median(dd[key]), 4))
        result["mean"].append(round(np.mean(dd[key]), 4))
        result["std"].append(round(np.std(dd[key]), 4))
        result["cnt"].append(round(len(dd[key]), 4))

    df = pd.DataFrame(result)
    book = Workbook()
    sheet = book.active
    for each in dataframe_to_rows(df, index=False, header=True):
        sheet.append(each)
    book.save(_path_ + "pr_ca_control_accuracy.xlsx")


def pr_rate_of_change_accuracy(_path_, _file_, clock_diff, speed_set):
    fd_ubx = open(_path_ + _file_, 'rb')
    result = {"sv": [], "min": [], "max": [], "median": [],
              "mean": [], "std": [], "cnt": []}
    delta_pr, _ = compare_adjacent(get_all_pr_ca(fd_ubx), False)
    pr_chane_rate = {}
    for key in delta_pr.keys():
        assert isinstance(delta_pr[key], list)
        pr_chane_rate[key] = []
    for key in delta_pr.keys():
        for i in range(len(delta_pr[key])):
            pr_chane_rate[key].append(delta_pr[key][i] - clock_diff - speed_set)
        result["sv"].append(key)
        result["min"].append(round(min(pr_chane_rate[key]), 4))
        result["max"].append(round(max(pr_chane_rate[key]), 4))
        result["median"].append(round(np.median(pr_chane_rate[key]), 4))
        result["mean"].append(round(np.mean(pr_chane_rate[key]), 4))
        result["std"].append(round(np.std(pr_chane_rate[key]), 4))
        result["cnt"].append(round(len(pr_chane_rate[key]), 4))
    df = pd.DataFrame(result)
    book = Workbook()
    sheet = book.active
    for each in dataframe_to_rows(df, index=False, header=True):
        sheet.append(each)
    book.save(_path_ + "pr_change_rate_accuracy.xlsx")


if __name__ == "__main__":
    path = r"D:\work\temp\1102" + "\\"
    # path_file = r"/home/kwq/work/lab_test/1102/COM7_211102_101911_F9P.ubx"
    # path_file = r"D:\work\temp\1102\COM7_211103_021622_satellite_fix_speed.ubx"
    file = r"COM7_211102_101911_F9P.ubx"
    file_move = "COM7_211103_021622_satellite_fix_speed.ubx"

    test = ChannelUniformityTest(path + file)
    test.channel_uniformity()

    pr_ca_control_accuracy(path, file)
    clk_diff = clock_diff(path, file)

    pr_rate_of_change_accuracy(path, file_move, clk_diff, 1000)
