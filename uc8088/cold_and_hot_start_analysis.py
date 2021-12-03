import re, os
from collections import deque


def hot_start_analysis(dir_file: str):
    """ 测试热启动灵敏度 ：
    板子正常功率下定位二十分钟，断电1小时， 信号功率拉低再上电。看能捕获到多低的信号 即为 测试热启灵敏度。
    由于板子一开始正常定位， 则开始的所有 GGA 中 都有  E,1, （坐标在东经才可）， 鉴于此，
    1、 找到 第一条 GGA 中 有 E,0, 的 语句，该时刻 板子刚刚上电。 然后 ：
    2、 找到 第一条 GSV 中 有 信噪比 的语句，该时刻 板子捕获到刚刚捕获到信号。 最后 ：
    3、 找到 第一条定位的 GGA 语句， 该时刻 板子 热启动 成功定位。 退出程序。
    """
    GGA_Flag = "GGA"
    GSV_Flag = "$GPGSV"
    cnr_idx = (7, 11, 15, 19)
    with open(path + file, 'r', errors="ignore") as fd:
        row_cnt = 0
        power_on_flag = 0
        gga = ''
        for row in fd:
            row_cnt += 1
            # if row_cnt > 40326:
            #     print(row)
            if GGA_Flag in row:
                gga = row
                if power_on_flag == 0 and "E,1," not in row:
                    power_on_flag = 1
                    print('\033[1;31m' + "power on , row cnt = {}".format(row_cnt) + '\033[0m')
                    print(row)
                if power_on_flag == 9 and "E,1," in row:
                    print('\033[1;32m' + "first fix row cnt = {}".format(row_cnt) + '\033[0m')
                    print(gga)
                    # sys.exit(0)
                    return

            if power_on_flag == 1 and GSV_Flag in row:
                if row.count(',') < 19:
                    # print(row_cnt, "row Incomplete ", row)
                    continue
                ret = row[:row.index("*")].split(',')
                for i in cnr_idx:
                    if ret[i]:
                        print(gga, end='')
                        print('\033[1;33m' + "first acq row cnt = {}".format(row_cnt) + '\033[0m')
                        print(row)
                        power_on_flag = 9
                        break


def get_sec_of_day_from_gga(gga: str):
    hhmmss = gga.split(',')[1]
    if hhmmss:
        hour = int(hhmmss[:2])
        minute = int(hhmmss[2:4])
        second = round(float(hhmmss[4:]))
        return hour * 3600 + minute * 60 + second
    else:
        return 0


def cold_start_analysis(dir_file: str, initial_signal_intensity=-148):
    """ 冷启动测试 ：
    板子接收到的 模拟器信号功率从 initial_signal_intensity (-148dB)开始， 每隔10分钟升高 1dB。 测试板子至少需要多强的信号才能定位。
    由于板子上电后模拟器才放信号， 故一开始 板子的时间 比 模拟器的时间大， 鉴于此：
    1、 找到 GGA 时间回退的语句， 该时刻即为板子拿到模拟器的时间。 根据该时刻，推算出模拟器的信号强度
    2、 找到第一条有 E,1, 的 GGA，（坐标在东经才可）， 该时刻即为板子首次有效定位。 退出程序。
    """
    GGA_mark = re.compile(r'\$G[PN]GGA')
    q = deque(maxlen=2)
    with open(path + file, 'r', errors="ignore") as fd:
        row_cnt = 0
        get_time_flag = 0

        for row in fd:
            row_cnt += 1
            if GGA_mark.match(row):
                q.append(row)

                if get_time_flag == 0:
                    sec_of_day = get_sec_of_day_from_gga(row)
                    if sec_of_day < get_sec_of_day_from_gga(q[0]):
                        get_time_flag = 1
                        initial_signal_intensity += sec_of_day // 600
                        print('\033[1;33m' + "{} dB get time , row cnt = {}".format(initial_signal_intensity, row_cnt)
                              + '\033[0m')
                        print(row)
                elif get_time_flag == 1:
                    if "E,1," in row:
                        sec_of_day = get_sec_of_day_from_gga(row)
                        initial_signal_intensity += sec_of_day // 600
                        print('\033[1;32m' + "{} dB fixed, row cnt = {}".format(initial_signal_intensity, row_cnt)
                              + '\033[0m')
                        print(row)
                        # sys.exit(0)
                        return
                else:
                    print('\033[1;31m' + "error!" + '\033[0m')


if __name__ == "__main__":
    # path = r"D:/Program Files/Serial Port Utility/LOG/1129/"
    path = r"E:\work\serial\1203\2_cold_start/"
    # file = "3_TAU1202_hot_start_154.txt"
    file_lst = [f for f in os.listdir(path) if f.endswith('txt') or f.endswith("log")]  # and f.startswith("14")]
    file_lst.sort()
    for file in file_lst:
        print("\n", file)
        # hot_start_analysis(path + file)
        cold_start_analysis(path + file)
