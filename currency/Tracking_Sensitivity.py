#!/usr/bin/env python3
"""
Analyze the tracking sensitivity of each receiver

The simulator signal drops gradually,
Record the last positioning time, the time when the signal-to-noise ratio of each satellite last appeared in the GSV
of the receiver,
This time is the tracking sensitivity

"""
import os
import matplotlib.pyplot as plt

time_power = {"0": 131, "15": 134, "16": 137, "17": 140, "18": 143,
              "19": 146, "20": 149, "21": 150, "22": 151, "23": 152,
              "24": 153, "25": 154, "26": 155, "27": 156, "28": 157,
              "29": 158, "30": 159, "31": 160, "32": 161, "33": 162,
              "34": 163, "35": 164, "36": 165, "37": 166, "38": 167,
              "39": 168, "40": 169, "41": 170, "42": 171}


def power_at_current_time(time_sec_) -> int:
    minute = time_sec_ // 60
    if minute < 15:
        return 131
    elif minute < 21:
        return (minute - 15) * 3 + time_power["15"]
    elif minute < 43:
        return (minute - 21) + time_power["21"]
    else:
        return 171


def get_epoch_nmea(_path_file_: str):
    is_finish = False
    epoch_lines = []
    with open(_path_file_, 'r', errors="ignore") as fd:
        for row in fd:
            if "GGA," in row:
                yield is_finish, epoch_lines
                epoch_lines.clear()
            epoch_lines.append(row)
    is_finish = True
    return is_finish, epoch_lines


def get_time_from_gga(row="$GPGGA,024028.00,4000.0013,N,11559.9974,E,1,10,1.22,113.714,M,-8.00,M,,*78"):
    """
    :param row:   GPGGA行
    :return:      sec_of_day,  original_str
    """
    GGA = row.split(',')
    time_str = GGA[1]
    if len(time_str) == 0:
        return -1, time_str
    time_sec = int(time_str[0:2]) * 3600 + int(time_str[2:4]) * 60 + float(time_str[4:])
    return time_sec, time_str


def parsing_gsv(_gsv_: str):
    # row_ = _gsv_[_gsv_.index('$GP'):]
    row_ = _gsv_[_gsv_.index("GSV,"):_gsv_.rindex("*")]
    ret = row_.split(',')

    total_sentence = int(ret[1])
    current_sentence = int(ret[2])
    total_sv = int(ret[3])

    ret_dd = {}

    if total_sentence == current_sentence:
        for i in range(4 - ((total_sentence * 4) - total_sv)):
            prn = ret[4 * i + 0 + 4]
            ele = ret[4 * i + 1 + 4]  # elevation
            if len(ele) == 0:
                ele = "0"
            azi = ret[4 * i + 2 + 4]  # azimuth
            if len(azi) == 0:
                azi = "0"
            cnr = ret[4 * i + 3 + 4]
            if len(cnr) == 0:
                cnr = "-1"
            ret_dd[prn] = (int(ele), int(azi), int(cnr))
    else:
        for i in range(4):
            prn = ret[4*i + 0 + 4]

            # if prn == "44":
            #     print('s')

            ele = ret[4*i + 1 + 4]  # elevation
            if len(ele) == 0:
                ele = "0"
            azi = ret[4*i + 2 + 4]  # azimuth
            if len(azi) == 0:
                azi = "0"
            cnr = ret[4*i + 3 + 4]
            if len(cnr) == 0:
                cnr = "-1"
            ret_dd[prn] = (int(ele), int(azi), int(cnr))
    return ret_dd


def get_all_cnr_from_gsv(_path_file_: str):
    all_gsv_cnr, epoch_valid_satellite_number = {}, {}

    time_sec, time_str = -1, ""
    begin = False
    for epoch_nmea in get_epoch_nmea(_path_file_):
        if epoch_nmea[0] is True:
            break
        epoch_gsv_info = {}
        for row in epoch_nmea[1]:
            if "GPGSV" in row:
                 epoch_gsv_info.update(parsing_gsv(row))
            elif "GGA" in row:
                if begin is False:
                    if "E,1," not in row:
                        time_sec = -1
                        break
                    else:
                        begin = True
                time_sec, time_str = get_time_from_gga(row)
                if time_sec == -1:
                    break

        if time_sec == -1:
            continue
        valid_satellite_cnt = 0
        for sv_prn in epoch_gsv_info.keys():
            if epoch_gsv_info[sv_prn][2] != -1:
                valid_satellite_cnt += 1
            if sv_prn in all_gsv_cnr.keys():
                if epoch_gsv_info[sv_prn][2] == -1:
                    if all_gsv_cnr[sv_prn][-1] != -1:
                        print("lose tracking time:", time_str, "single power ", power_at_current_time(time_sec),
                              " sv:", sv_prn, epoch_gsv_info[sv_prn])
                    # else:
                    #     continue
                all_gsv_cnr[sv_prn] += [time_sec, epoch_gsv_info[sv_prn][2]]
            else:
                all_gsv_cnr[sv_prn] = [time_sec, epoch_gsv_info[sv_prn][2]]
        epoch_valid_satellite_number[time_sec] = valid_satellite_cnt
    return all_gsv_cnr, epoch_valid_satellite_number


def tacking_analysis_base_gsv(_path_file_: str):
    all_cnr, valid_satellite_number = get_all_cnr_from_gsv(_path_file_)

    (filepath, tempfilename) = os.path.split(_path_file_)
    (filename, extension) = os.path.splitext(tempfilename)

    # for key in all_cnr.keys():
    #     x = all_cnr[key][0::2]
    #     y = all_cnr[key][1::2]
    #     plt.plot(x, y, marker='x', label=key)
    #     plt.legend()  # 不加该语句无法显示 label
    # plt.show()

    x = list(valid_satellite_number.keys())[900:]
    y = list(valid_satellite_number.values())[900:]

    last_num = y[0]
    power__sv_num = {power_at_current_time(x[0]): last_num}
    for time_sec in x:
        current_sv_num = valid_satellite_number[time_sec]
        power_now = power_at_current_time(time_sec)
        if current_sv_num < last_num:
            power__sv_num[power_now] = current_sv_num
        last_num = current_sv_num
        if time_sec % 60 == 0:
            plt.vlines(int(time_sec), 0, current_sv_num, 'r', "--")
            plt.text(time_sec, 0, "-" + str(int(power_now)))
    print(power__sv_num)

    plt.title(filename + "\nepoch time valid satellite number")
    plt.xlabel("time (s)")
    plt.ylabel("satellite number")

    plt.plot(x, y, marker='x')

    plt.show()


if __name__ == "__main__":
    # path = "/home/kwq/work/lab_test/2022/0221/"
    path = "d:/work/lab_test/2022/0221/"
    file_lst = [f for f in os.listdir(path) if f.endswith("log") or f.endswith("ubx")]
    # file_lst = [f for f in os.listdir(path) if f.endswith("ubx")]

    for f in file_lst:
        print("\n\n", f)
        tacking_analysis_base_gsv(path + f)
