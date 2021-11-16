from collections import deque
import sys
import os
import re


path = r"D:\work\temp\1028" + "\\"
ubx_file = "COM3_211028_042604_M8T.ubx"
# simulator_file = [f for f in os.listdir(path) if f.endswith(").TXT")]
simulator_file = r"中央公园广场.RSIM_(M1B1-GPS_L1)_RawNav(20211028-1225).dat.TXT"


def dynamic_fd(p: str, file_lst: list):
    for f in file_lst:
        sv_id = re.findall(r"\d+", f[f.index(".dat"):])[0]
        exec('fd_{}={}'.format(sv_id, open(p + f, 'r')))


def search(lines, time_sec_of_week, GNSS_SYS=0, history=15):
    satellite_sys_time_step = {0: 6, 3: 18000}
    time_sow = time_sec_of_week
    previous_lines = deque(maxlen=history)
    for line in lines:
        if time_sow == time_sec_of_week:
            time_sow = int(line.split()[5])
        if time_sow != int(line.split()[5]):
            yield previous_lines
            previous_lines.clear()
            time_sow = int(time_sow) + satellite_sys_time_step[GNSS_SYS]
        previous_lines.append(line)
    # sys.exit()


def gps_original_raw_to_words(original_raw: str) -> list:
    ret = []
    if len(original_raw) != 75:
        return ret
    raw = int(original_raw, 16)
    for i in range(1, 11):
        ret.append((raw >> (300 - i * 30)) & 0x3fffffff)
    return ret


def get_epoch_raw_from_simulator(stream, begin_time=86400, sys=0, length=18):
    for epoch_lines in search(stream, begin_time, sys, length):
        prn_words = {}      # {svID: [word1, word2, ... , word10]}
        for row in epoch_lines:
            ll = row.split()
            if sys == 0:
                prn_words[ll[1]] = gps_original_raw_to_words(ll[6])
            else:
                prn_words[ll[1]] = (int(ll[5][:-3]), ll[6])    # 时间精度是 ms
        yield prn_words
    # sys.exit()


if __name__ == "__main__":
    # for msg in get_raw_word_from_ubx(path + ubx_file):
    #     print(msg)
    # second_of_week = 86400

    # with open(path + simulator_file, 'r') as f_sim:
    #     for prevlines in search(f_sim, second_of_week, 15):
    #         svId_words = {}
    #         for line in prevlines:
    #             print(line, end='')
    #         print("---"*30)

    for dd in get_epoch_raw_from_simulator(path + simulator_file):
        key_list = list(dd.keys())
        sow = dd[key_list[0]][1] >> 13
        g_dd = dd
        print(sow)


