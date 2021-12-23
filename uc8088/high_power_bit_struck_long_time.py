from collections import deque
import subprocess as sp
import re
import os
eva_file = '/home/ucchip/Desktop/tmp_file/_tmp_pr.txt'


def ACQ_SP_ir_span():
    q = deque(maxlen=2)
    with open(eva_file, 'r', errors="ignore") as fd:
        row_cnt, ab_row = 0, 0
        for row in fd:
            row_cnt += 1
            q.append(row)
            if len(q) == 2:
                now_row = q[1]
                pre_row = q[0]
                try:
                    now_ll = re.findall(r"\d+", now_row)
                    pre_ll = re.findall(r"\d+", pre_row)
                except:
                    continue
                if int(now_ll[1]) == 10:
                    continue
                now_ir_cnt = int(now_ll[2])
                pre_ir_cnt = int(pre_ll[2])
                if now_ir_cnt - pre_ir_cnt > 200:
                    ab_row += 1
                    print(row)
    print('\033[1;33m' + "abnormal rate = {:.2%}".format(ab_row / row_cnt) + '\033[0m')


def extract_tgt(fpath):
    sp.check_output("grep -an 'ACQ EFFICIENCY,' {} > {}".format(fpath, eva_file), shell=True)


if __name__ == "__main__":
    fdir = "/home/ucchip/KWQ/gps_test/1210/"
    file_list = [f for f in os.listdir(fdir) if f.endswith('.log') and ("_-115" in f or "_-125" in f or "_-110" in f)]
    file_list.sort()
    for file in file_list:
        print(file)
        extract_tgt(fdir + file)
        ACQ_SP_ir_span()
        print()
