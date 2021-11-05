"""
use F9P test simulator Signal accuracy
用F9P 测试模拟器 的信号精度
"""

import sys
import matplotlib.pyplot as plt
from ubxTranslate.UBX_RXM import get_epoch_RAWX_from_ubx
from ubxTranslate.core import Parser
from ubxTranslate.predefined import RXM_CLS
import numpy as np
import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
GPS_SYS = 0


def print_mean_mid_95_99(ll: list, head="通道一致性", tail="max - min"):
    assert isinstance(ll, list)
    length = len(ll)
    assert length > 0
    mean_ll = np.mean(ll)
    mid_ll = np.median(ll)
    list_95 = ll[int(length * 0.95)]
    list_99 = ll[int(length * 0.99)]
    print("{:<20s} {:>11.3f} {:>11.3f} {:>11.3f} {:>11.3f} {:^33s}".format(
        head, mean_ll, mid_ll, list_95, list_99, tail))


class ChannelUniformityTest:
    def __init__(self, dir_file):
        self.dir_file = dir_file
        try:
            self.fd = open(dir_file, 'rb')
        except:
            print("open ", dir_file, " error")
            sys.exit(-1)

    def channel_uniformity(self):
        """通道一致性测试: 两种判决标准
        1、 [相邻历元所有通道伪距差  的 最大值 - 最小值] 对该列表求均值、中位数、 95%、 99%
        2、 [相邻历元所有通道伪距差  的 标准差 ] 对该列表求均值、中位数、 95%、 99%
        """
        pr_diff_list = []
        pr_std_list = []
        for d in get_epoch_RAWX_from_ubx(self.fd, GPS_SYS):
            pr_lst = []
            for k in d.keys():
                pr_lst.append(d[k].prMes)
            pr_diff_list.append(max(pr_lst) - min(pr_lst))
            pr_std_list.append(np.std(pr_lst))

        print_mean_mid_95_99(pr_diff_list)
        print_mean_mid_95_99(pr_std_list, "通道一致性", "std")


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


def compare_adjacent_epoch_split_by_prn(l: list, ca_flag=True):
    """
    return {卫星号： [相邻伪距差]}, {卫星号: [相邻载波（个数）差]}
    """
    length = len(l)
    # print("epoch total =", length)
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
            delta_pr[key].append(abs(epoch_next[key][0] - epoch_now[key][0]))
            if ca_flag:
                delta_ca[key].append(abs(epoch_next[key][1] - epoch_now[key][1]))
    return delta_pr, delta_ca


def compare_adjacent_epoch(l: list, ca_flag=True):
    """
    return [所有通道相邻历元伪距差 的均值], [所有通道相邻历元载波（个数）差 的均值]
    """
    length = len(l)
    # print("epoch total =", length)
    assert isinstance(l[0], dict)
    delta_pr_mean = []
    delta_ca_mean = []
    for key in l[0].keys():
        assert isinstance(l[0][key], tuple)
    for i in range(length - 1):
        epoch_now: dict = l[i]
        epoch_next: dict = l[i + 1]
        diff_pr_epoch = []
        diff_ca_epoch = []
        for key in epoch_now.keys():
            diff_pr_epoch.append(abs(epoch_next[key][0] - epoch_now[key][0]))
            if ca_flag:
                diff_ca_epoch.append(abs(epoch_next[key][1] - epoch_now[key][1]))
        delta_pr_mean.append(np.mean(diff_pr_epoch))
        if ca_flag:
            delta_ca_mean.append(np.mean(diff_ca_epoch))
    return delta_pr_mean, delta_ca_mean


def clock_diff(_path_, _file_):
    """计算 ublox 钟漂
    """
    fd_ubx = open(_path_ + _file_, 'rb')
    delta_pr, _ = compare_adjacent_epoch(get_all_pr_ca(fd_ubx), False)
    assert isinstance(delta_pr, list)
    # clock_diff_lst = []
    # for i in range(len(delta_pr) - 1):
    #     clock_diff_lst.append(delta_pr[i + 1] - delta_pr[i])
    plt.plot([x for x in range(len(delta_pr))], delta_pr, marker='x')
    # plt.show()
    plt.draw()
    plt.pause(5)
    plt.close()
    return np.mean(delta_pr), np.std(delta_pr)


# def diff_delta_pr_delta_ca_prn(delta_pr: dict, delta_ca: dict) -> dict:
#     """
#     相邻伪距差 - 相邻载波（个数）差 * 波长
#     """
#     assert isinstance(delta_pr, dict)
#     assert isinstance(delta_ca, dict)
#     wavelength = 3e8 / 1575420000
#     diff_pr_ca = {}
#     for key in delta_pr.keys():
#         assert len(delta_pr[key]) == len(delta_ca[key])
#         diff_pr_ca[key] = []
#         for i in range(len(delta_pr[key])):
#             diff_pr_ca[key].append(delta_pr[key][i] - wavelength * delta_ca[key][i])
#     return diff_pr_ca
#
#
# def pr_ca_control_accuracy_prn(_path_, _file_):
#     """
#     载波相位控制精度
#     """
#     result = {"sv": [], "min": [], "max": [], "median": [],
#               "mean": [], "std": [], "cnt": []}
#     fd_ubx = open(_path_ + _file_, 'rb')
#     ret_pr, ret_ca = compare_adjacent_epoch_split_by_prn(get_all_pr_ca(fd_ubx))
#     dd = diff_delta_pr_delta_ca_prn(ret_pr, ret_ca)
#     for key in dd.keys():
#         result["sv"].append(key)
#         result["min"].append(round(min(dd[key]), 4))
#         result["max"].append(round(max(dd[key]), 4))
#         result["median"].append(round(np.median(dd[key]), 4))
#         result["mean"].append(round(np.mean(dd[key]), 4))
#         result["std"].append(round(np.std(dd[key]), 4))
#         result["cnt"].append(round(len(dd[key]), 4))
#
#     df = pd.DataFrame(result)
#     book = Workbook()
#     sheet = book.active
#     for each in dataframe_to_rows(df, index=False, header=True):
#         sheet.append(each)
#     book.save(_path_ + "pr_ca_control_accuracy.xlsx")
#
#
# def pr_rate_of_change_accuracy_prn(_path_, _file_, clock_diff, speed_set):
#     fd_ubx = open(_path_ + _file_, 'rb')
#     result = {"sv": [], "min": [], "max": [], "median": [],
#               "mean": [], "std": [], "cnt": []}
#     delta_pr, _ = compare_adjacent_epoch_split_by_prn(get_all_pr_ca(fd_ubx), False)
#     pr_chane_rate = {}
#     for key in delta_pr.keys():
#         assert isinstance(delta_pr[key], list)
#         pr_chane_rate[key] = []
#     for key in delta_pr.keys():
#         for i in range(len(delta_pr[key])):
#             pr_chane_rate[key].append(delta_pr[key][i] + clock_diff - speed_set)
#         result["sv"].append(key)
#         result["min"].append(round(min(pr_chane_rate[key]), 4))
#         result["max"].append(round(max(pr_chane_rate[key]), 4))
#         result["median"].append(round(np.median(pr_chane_rate[key]), 4))
#         result["mean"].append(round(np.mean(pr_chane_rate[key]), 4))
#         result["std"].append(round(np.std(pr_chane_rate[key]), 4))
#         result["cnt"].append(round(len(pr_chane_rate[key]), 4))
#     df = pd.DataFrame(result)
#     book = Workbook()
#     sheet = book.active
#     for each in dataframe_to_rows(df, index=False, header=True):
#         sheet.append(each)
#     book.save(_path_ + "pr_change_rate_accuracy.xlsx")


def pr_rate_of_change_accuracy(_path_, _file_, clk_diff, speed_set):
    """伪距变化率"""
    fd_ubx = open(_path_ + _file_, 'rb')
    l = get_all_pr_ca(fd_ubx)
    length = len(l)
    assert isinstance(l[0], dict)
    max_diff_delta_pr_diff_clk_speed = []
    std_delta_pr_diff_clk_speed = []
    for key in l[0].keys():
        assert isinstance(l[0][key], tuple)
    for i in range(length - 1):
        epoch_now: dict = l[i]
        epoch_next: dict = l[i + 1]
        delta_pr_diff_clk_speed = []
        for key in epoch_now.keys():
            delta_pr = abs(epoch_next[key][0] - epoch_now[key][0])
            delta_pr_diff_clk_speed.append(delta_pr + clk_diff - speed_set)

        max_diff_delta_pr_diff_clk_speed.append(max(delta_pr_diff_clk_speed) - min(delta_pr_diff_clk_speed))
        std_delta_pr_diff_clk_speed.append(np.std(delta_pr_diff_clk_speed))

    print_mean_mid_95_99(max_diff_delta_pr_diff_clk_speed, "伪距变化率", "max-min")
    print_mean_mid_95_99(std_delta_pr_diff_clk_speed, "伪距变化率", "std")


def max_diff_and_std_epoch_diff_delta_pr_delta_ca(l: list, frequency=1575420000):
    """
    相邻伪距差 - 相邻载波（个数）差 * 波长
    """
    wavelength = 3e8 / frequency
    length = len(l)
    assert isinstance(l[0], dict)
    max_diff_diff_pr_ca = []
    std_diff_pr_ca = []
    for key in l[0].keys():
        assert isinstance(l[0][key], tuple)
    for i in range(length - 1):
        epoch_now: dict = l[i]
        epoch_next: dict = l[i + 1]
        epoch_diff_pr_ca = []
        for key in epoch_now.keys():
            diff_pr = abs(epoch_next[key][0] - epoch_now[key][0])
            diff_ca = abs(epoch_next[key][1] - epoch_now[key][1])
            epoch_diff_pr_ca.append(diff_pr - diff_ca * wavelength)
        max_diff_diff_pr_ca.append(max(epoch_diff_pr_ca) - min(epoch_diff_pr_ca))
        std_diff_pr_ca.append(np.std(epoch_diff_pr_ca))
    return max_diff_diff_pr_ca, std_diff_pr_ca


def pr_ca_control_accuracy_prn(_path_, _file_):
    """
    载波相位控制精度
    """
    fd_ubx = open(_path_ + _file_, 'rb')
    max_diff, std = max_diff_and_std_epoch_diff_delta_pr_delta_ca(get_all_pr_ca(fd_ubx), 1575420000)
    print_mean_mid_95_99(max_diff, "PR-CA控制精度", "[epoch_max_diff[prn_deltaPR - prn_deltaCA]]")
    print_mean_mid_95_99(std, "PR-CA控制精度", "[epoch_std[prn_deltaPR - prn_deltaCA]]")


if __name__ == "__main__":
    # path = r"D:\work\temp\1102" + "\\"
    path = r"/home/kwq/work/lab_test/1104/"
    # path_file = r"/home/kwq/work/lab_test/1102/COM7_211102_101911_F9P.ubx"
    # path_file = r"D:\work\temp\1102\COM7_211103_021622_satellite_fix_speed.ubx"
    # file = r"COM7_211102_101911_F9P.ubx"
    file = "COM14___115200_211104_082229_fixPR.ubx"
    file_move = "COM14___115200_211104_085043_satellite_speed1000.ubx"
    print("{:<20s} {:>12s} {:>12s} {:>12s} {:>12s} {:^12s}".format("项目", "mean", "mid", "95%", "99%", "判决方式"))
    test = ChannelUniformityTest(path + file)
    test.channel_uniformity()

    pr_ca_control_accuracy_prn(path, file)

    clk_diff_mean, clk_diff_std = clock_diff(path, file)
    print("钟漂 mean =", clk_diff_mean, "  std =", clk_diff_std)
    pr_rate_of_change_accuracy(path, file_move, clk_diff_mean, 1000)
