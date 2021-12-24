import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator
from ubxTranslate.UBX_RXM import get_epoch_RAWX_from_ubx, get_epoch_MEASX_from_ubx
import sys
import logging
import numpy as np
import pandas as pd

logging.basicConfig(level=logging.DEBUG, format='%(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
# format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')


def dict_to_broken(d_: dict):
    dddd = {}
    for key in d_.keys():
        flag, t = 0, 0
        arr = []
        for i in d_[key]:
            if i == 1:
                if flag == 1:
                    arr[-1][-1] += 1
                else:
                    arr.append([t, 1])
                flag = 1
            elif i == 0:
                flag = 0
            else:
                raise Exception
            t += 1
        dddd[key] = arr
    return dddd


def dict_to_keep_time(d_: dict):
    ddd = {}
    for key in d_.keys():
        flag = 0
        ddd[key] = []
        for i in d_[key]:
            if i == 1:
                if flag == 1:
                    ddd[key][-1] += 1
                else:
                    ddd[key].append(1)
                flag = 1
            elif i == 0:
                flag = 0
            else:
                raise Exception
    return ddd


def pfa_ubx_test(path_file_, rawx=True):
    try:
        fd_ = open(path_file_, 'rb')
    except:
        print("open ", path_file_, " error")
        sys.exit(-1)
    ff = get_epoch_MEASX_from_ubx
    if rawx:
        ff = get_epoch_RAWX_from_ubx

    time_sec, time_bak, total_satellite, false_satellite, true_satellite = 0, 0, 0, 0, 0
    false_satellite_cnt_list = []
    true_satellite_cnt_list = []
    false_satellite_cnt_dict = {}
    result = {"used time": [], "true satellite": [], "false satellite": [],
              "false_satellite mean": [], "false_satellite median": []}
    false_satellite_keep_dict = {}

    for dd in ff(fd_):
        temp_false, temp_true = 0, 0
        time_sec += 1
        if dd:
            for key in dd.keys():
                if key < 31:
                    false_satellite += 1
                    temp_false += 1
                    if key in false_satellite_cnt_dict.keys():
                        if len(false_satellite_cnt_dict[key]) == len(result["used time"])+1:
                            false_satellite_cnt_dict[key][-1] += 1
                        elif len(false_satellite_cnt_dict[key]) == len(result["used time"]):
                            false_satellite_cnt_dict[key].append(1)
                        else:
                            raise Exception
                    else:
                        false_satellite_cnt_dict[key] = []
                        while len(false_satellite_cnt_dict[key]) != len(result["used time"]):
                            false_satellite_cnt_dict[key].append(0)
                        false_satellite_cnt_dict[key].append(1)

                    if key in false_satellite_keep_dict.keys():
                        while len(false_satellite_keep_dict[key]) < time_sec:
                            false_satellite_keep_dict[key].append(0)
                        false_satellite_keep_dict[key].append(1)
                    else:
                        false_satellite_keep_dict[key] = []
                        while len(false_satellite_keep_dict[key]) < time_sec:
                            false_satellite_keep_dict[key].append(0)
                        false_satellite_keep_dict[key].append(1)
                else:
                    true_satellite += 1
                    temp_true += 1
                total_satellite += 1
            false_satellite_cnt_list.append(temp_false)
            true_satellite_cnt_list.append(temp_true)
        else:
            if false_satellite_cnt_list and true_satellite_cnt_list:
                logging.debug("\033[1;36m" +
                              "used time = {},true satellite cnt = {}, false satellite cnt = {}, mean = {}, median = {}"
                              .format(time_sec - time_bak, np.sum(true_satellite_cnt_list),
                                      np.sum(false_satellite_cnt_list), np.mean(false_satellite_cnt_list),
                                      np.median(false_satellite_cnt_list)) + "\033[0m")
                result["used time"].append(time_sec - time_bak)
                result["true satellite"].append(np.sum(true_satellite_cnt_list))
                result["false satellite"].append(np.sum(false_satellite_cnt_list))
                result["false_satellite mean"].append(np.mean(false_satellite_cnt_list))
                result["false_satellite median"].append(np.median(false_satellite_cnt_list))

                false_satellite_cnt_list.clear()
                true_satellite_cnt_list.clear()
                for key in false_satellite_cnt_dict.keys():
                    if len(false_satellite_cnt_dict[key]) != len(result["used time"]):
                        false_satellite_cnt_dict[key].append(0)
                for key in false_satellite_keep_dict.keys():
                    while len(false_satellite_keep_dict[key]) < time_sec:
                        false_satellite_keep_dict[key].append(0)
            time_bak = time_sec
    if false_satellite_cnt_list and true_satellite_cnt_list:
        logging.debug("\033[1;36m" +
                      "used time = {},true satellite cnt = {}, false satellite cnt = {}, mean = {}, median = {}"
                      .format(time_sec - time_bak, np.sum(true_satellite_cnt_list),
                              np.sum(false_satellite_cnt_list), np.mean(false_satellite_cnt_list),
                              np.median(false_satellite_cnt_list)) + "\033[0m")
        result["used time"].append(time_sec - time_bak)
        result["true satellite"].append(np.sum(true_satellite_cnt_list))
        result["false satellite"].append(np.sum(false_satellite_cnt_list))
        result["false_satellite mean"].append(np.mean(false_satellite_cnt_list))
        result["false_satellite median"].append(np.median(false_satellite_cnt_list))
        time_bak = time_sec
        false_satellite_cnt_list.clear()
        true_satellite_cnt_list.clear()
        for key in false_satellite_cnt_dict.keys():
            if len(false_satellite_cnt_dict[key]) != len(result["used time"]):
                false_satellite_cnt_dict[key].append(0)
        for key in false_satellite_keep_dict.keys():
            while len(false_satellite_keep_dict[key]) < time_sec:
                false_satellite_keep_dict[key].append(0)
    # dddd = dict_to_broken(false_satellite_keep_dict)
    # tmp = 0
    # for key in dddd.keys():
    #     plt.broken_barh(dddd[key], (int(key) + 0.7, 0.5))
    #     tmp += 1
    # y_major_locator = MultipleLocator(1)
    # ax = plt.gca()
    # ax.yaxis.set_major_locator(y_major_locator)
    # plt.show()
    false_satellite_keep_time_dict = dict_to_keep_time(false_satellite_keep_dict)
    # sorted_false_satellite_keep_time_dict = dict(sorted(sorted(false_satellite_keep_time_dict.items(), key=lambda kv:(kv[0], kv[1]))))
    # for key in false_satellite_keep_time_dict.keys():
    #     print("sv {} keep time mean = {:.1f} s  , median = {}".format(key, np.mean(false_satellite_keep_time_dict[key]), np.median(false_satellite_keep_time_dict[key])))
    out_str = "           sv   "
    sorted_key = sorted(false_satellite_keep_time_dict)
    for key in sorted_key:
        out_str += "{:^5}".format(key)
    out_str += "\n{:^17s}".format("keep time mean")
    for key in sorted_key:
        out_str += "{:^5.1f}".format(np.mean(false_satellite_keep_time_dict[key]))
    out_str += "\n{:<17s}".format("keep time median")
    for key in sorted_key:
        out_str += "{:^5.1f}".format(np.median(false_satellite_keep_time_dict[key]))
    print(out_str)
    result.update(false_satellite_cnt_dict)
    df = pd.DataFrame(result)
    if rawx:
        df.to_excel(path + "PFA_base_rawx.xls", index=False)
    else:
        df.to_excel(path + "PFA_base_measx.xls", index=False)
    print("time = {}, true_satellite = {}, false_satellite = {}, total_satellite = {}"
          .format(time_sec, true_satellite, false_satellite, total_satellite))


def pad_ubx_by_gsv(path_file_):
    try:
        fd_ = open(path_file_, 'r', errors="ignore")
    except:
        print("open ", path_file_, " error")
        sys.exit(-1)
    reset_flag = 1
    sv_idx = (4, 8, 12, 16)
    cnr_idx = (7, 11, 15, 19)

    time_sec, time_bak, total_satellite, false_satellite, true_satellite = 0, 0, 0, 0, 0
    false_satellite_cnt_list = []
    true_satellite_cnt_list = []
    false_satellite_cnt_dict = {}
    false_satellite_keep_dict = {}
    result = {"used time": [], "true satellite": [], "false satellite": [],
              "false_satellite mean": [], "false_satellite median": []}
    temp_false, temp_true = 0, 0
    for row in fd_:
        if "$GNGGA" in row:
            row = row[row.index('$GN'):]
            if "GGA,," in row:
                if reset_flag == 1:
                    continue
                reset_flag = 1
                if false_satellite_cnt_list and true_satellite_cnt_list:
                    logging.debug("\033[1;36m" +
                                  "used time = {},true satellite cnt = {}, false satellite cnt = {}, mean = {}, median = {}"
                                  .format(time_sec - time_bak, np.sum(true_satellite_cnt_list),
                                          np.sum(false_satellite_cnt_list), np.mean(false_satellite_cnt_list),
                                          np.median(false_satellite_cnt_list)) + "\033[0m")
                    result["used time"].append(time_sec - time_bak)
                    result["true satellite"].append(np.sum(true_satellite_cnt_list))
                    result["false satellite"].append(np.sum(false_satellite_cnt_list))
                    result["false_satellite mean"].append(np.mean(false_satellite_cnt_list))
                    result["false_satellite median"].append(np.median(false_satellite_cnt_list))
                    false_satellite_cnt_list.clear()
                    true_satellite_cnt_list.clear()
                    for key in false_satellite_cnt_dict.keys():
                        if len(false_satellite_cnt_dict[key]) != len(result["used time"]):
                            false_satellite_cnt_dict[key].append(0)
                time_bak = time_sec
            else:
                reset_flag = 0
                if temp_true:
                    false_satellite_cnt_list.append(temp_false)
                    true_satellite_cnt_list.append(temp_true)
            time_sec += 1
            temp_false, temp_true = 0, 0
        elif "$GPGSV" in row:
            if reset_flag:
                continue
            else:
                row = row[row.index('$GP'):]
                ret = row.split(',')
                total_sentence = int(ret[1])
                current_sentence = int(ret[2])
                total_sv = int(ret[3])
                if total_sentence == current_sentence:    # last GSV
                    if row.count(',') != 19 - 4*((total_sentence * 4) - total_sv):
                        continue
                else:
                    if row.count(',') != 19:
                        continue
                ret = row[:row.index('*')].split(',')
                for i in range(len(sv_idx)):
                    if total_sentence == current_sentence:
                        if i >= 4 - ((total_sentence * 4) - total_sv):      # attention i = 0, 1, 2, 3
                            break
                    if ret[sv_idx[i]] and ret[cnr_idx[i]]:
                        prn = int(ret[sv_idx[i]])
                        if prn < 31:
                            false_satellite += 1
                            temp_false += 1
                            if prn in false_satellite_cnt_dict.keys():
                                if len(false_satellite_cnt_dict[prn]) == len(result["used time"]) + 1:
                                    false_satellite_cnt_dict[prn][-1] += 1
                                elif len(false_satellite_cnt_dict[prn]) == len(result["used time"]):
                                    false_satellite_cnt_dict[prn].append(1)
                                else:
                                    raise Exception
                            else:
                                false_satellite_cnt_dict[prn] = []
                                while len(false_satellite_cnt_dict[prn]) != len(result["used time"]):
                                    false_satellite_cnt_dict[prn].append(0)
                                false_satellite_cnt_dict[prn].append(1)

                            if prn in false_satellite_keep_dict.keys():
                                while len(false_satellite_keep_dict[prn]) < time_sec - 1:
                                    false_satellite_keep_dict[prn].append(0)
                                false_satellite_keep_dict[prn].append(1)
                            else:
                                false_satellite_keep_dict[prn] = []
                                while len(false_satellite_keep_dict[prn]) < time_sec-1:
                                    false_satellite_keep_dict[prn].append(0)
                                false_satellite_keep_dict[prn].append(1)
                        else:
                            true_satellite += 1
                            temp_true += 1
                        total_satellite += 1
    if false_satellite_cnt_list and true_satellite_cnt_list:
        logging.debug("\033[1;36m" +
                      "used time = {},true satellite cnt = {}, false satellite cnt = {}, mean = {}, median = {}"
                      .format(time_sec - time_bak, np.sum(true_satellite_cnt_list),
                              np.sum(false_satellite_cnt_list), np.mean(false_satellite_cnt_list),
                              np.median(false_satellite_cnt_list)) + "\033[0m")
        result["used time"].append(time_sec - time_bak)
        result["true satellite"].append(np.sum(true_satellite_cnt_list))
        result["false satellite"].append(np.sum(false_satellite_cnt_list))
        result["false_satellite mean"].append(np.mean(false_satellite_cnt_list))
        result["false_satellite median"].append(np.median(false_satellite_cnt_list))
        time_bak = time_sec
        false_satellite_cnt_list.clear()
        true_satellite_cnt_list.clear()
        for key in false_satellite_cnt_dict.keys():
            if len(false_satellite_cnt_dict[key]) != len(result["used time"]):
                false_satellite_cnt_dict[key].append(0)
        for key in false_satellite_keep_dict.keys():
            while len(false_satellite_keep_dict[key]) < time_sec-1:
                false_satellite_keep_dict[key].append(0)
    false_satellite_keep_time_dict = dict_to_keep_time(false_satellite_keep_dict)
    out_str = "           sv   "
    sorted_key = sorted(false_satellite_keep_time_dict)
    for key in sorted_key:
        out_str += "{:^5}".format(key)
    out_str += "\n{:^17s}".format("keep time mean")
    for key in sorted_key:
        out_str += "{:^5.1f}".format(np.mean(false_satellite_keep_time_dict[key]))
    out_str += "\n{:<17s}".format("keep time median")
    for key in sorted_key:
        out_str += "{:^5.1f}".format(np.median(false_satellite_keep_time_dict[key]))
    print(out_str)
    result.update(false_satellite_cnt_dict)
    df = pd.DataFrame(result)

    df.to_excel(path + "PFA_base_gsv.xls", index=False)

    print("time = {}, true_satellite = {}, false_satellite = {}, total_satellite = {}"
          .format(time_sec, true_satellite, false_satellite, total_satellite))


if __name__ == '__main__':
    path = r'/home/kwq/work/lab_test/1218/'
    # file = "ReceivedTofile-COM3-2021-12-13_15-52-22.DAT"
    file = "ReceivedTofile-COM3-2021-12-18_12-05-09_pwr115_sv31_32.DAT"
    # file = "ReceivedTofile-COM3-2021-12-14_18-31-53_pwr115.DAT"
    # file = "ReceivedTofile-COM3-2021-12-16_16-13-02_pwr115.DAT"
    pad_ubx_by_gsv(path + file)
    pfa_ubx_test(path + file)
    pfa_ubx_test(path + file, False)
