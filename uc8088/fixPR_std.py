"""
伪距精度测试
"""

import re
import math
import numpy as np
import matplotlib.pyplot as plt

#path = "/home/jqiu/gps_test_log/0114/"
#path = "/home/jqiu/share/th_tmp/"
path = "/home/ucchip/KWQ/gps_test/2022/0119/"
name = "4_mdl_TCXO_220119152457_trkLP.log"
# path = "/home/kwq/gps_test/0602/"
# name = "3_qfn8_fixPR_morePATH_pwr125_135.log"
TGT_CHL = 8
CHL_DEV = []
with open(path+name, 'r', errors="ignore") as fd:
    cnt = 0
    valid_sv_idx = []
    PR = []
    time = []
    result = []
    maxmin = []
    for row_idx, row in enumerate(fd):
        if "GGA" in row:
            time_hms = row[row.index(',')+1:row.index('.')]

        if "pli a:" in row: #and "TASK," in row:
            valid_sv_idx = []
            rec = re.findall(r"\d+", row)#[:row.index('TASK')])
            for i in range(10):
                if rec[i] != '100':
                    valid_sv_idx.append(i)
                # if rec[i] != '100' and i != 4:
                # valid_sv_idx.append(i)

        if 'CHL PR,' in row and "ir" in row:
            cnt += 1
            valid_PR = []
            # PR = re.findall(r"\d+\.?\d?", row[:row.index('ir')])
            PR = re.findall(r"\d+\.?\d*", row[:row.index('ir')])
            tgt_pr = 0
            for i in valid_sv_idx:
                try:
                    tmp = float(PR[i])
                except:
                    print(row)
                # if 1.5e7 < tmp < 3e7:
                valid_PR.append(tmp)
                #     if i == TGT_CHL:
                #         tgt_pr = tmp

            if valid_PR:
                res = np.std(np.array(valid_PR))
                if tgt_pr != 0:
                    CHL_DEV.append(tgt_pr - np.mean(np.array(valid_PR)))
                if res > 10000:
                    # print("ERROR!" + row)
                    pass
                else:
                    if res > 40:
                        print("ERROR!" + row)
                        continue
                    # print("time:", time_hms, cnt, ": ", res)
                    time.append(cnt)
                    result.append(res)
                    maxmin.append(max(valid_PR) - min(valid_PR))
            PR = []
    print("Final ave pr std {}".format(np.mean(result)))
    plt.plot(time, result, color='red', marker='*')
    plt.xlabel("epo cnt")
    plt.ylabel("pr std (m)")
    plt.title("pr std in fix pr scene(B1C)")
    '''if CHL_DEV:
        plt.figure()
        plt.plot([x for x in range(len(CHL_DEV))], CHL_DEV, color='red', marker='*')'''

#
    '''name = "0924_1248.log"
with open(path+name, 'r', encoding="ISO-8859-1") as fd:
    cnt = 0
    PR = []
    time = []
    result = []
    for row in fd:
        if "GGA" in row:
            pass
        if "CHL PR," in row and ", ir" in row:
            cnt += 1

            PR = re.findall("\d+\.\d+", row[:row.index('ir')])
            res = np.std(np.array([float(i) for i in PR]))
            if res == 0 or res > 10000:
                pass
            else:
                print(cnt, ": ", res)
                time.append(cnt)
                result.append(res)
            PR = []
    plt.figure()
    plt.plot(time, result, color='green', marker='*')'''
    plt.show()
    print("std =", np.std(result), "mean =", np.mean(result))

    plt.figure()
    plt.plot(time, maxmin, color='red', marker='*')
    plt.xlabel("epo cnt")
    plt.ylabel("mm pr diff (m)")
    plt.title("max-min in fix pr scene(GPS)")
    plt.show()
    print("std =", np.std(maxmin), "mean =", np.mean(maxmin))