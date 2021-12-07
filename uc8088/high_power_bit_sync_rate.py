import os, re
import numpy as np


def find_the_abnormal_items_idx(arr: list):
    m = np.median(arr)
    diff_m = []
    for idx, item in enumerate(arr):
        diff_m.append(np.fabs(item - m))
    return diff_m.index(max(diff_m))


def CHL_PR_get_pr(row_pr: str) -> list:
    str_PR = row_pr[:row_pr.index("ir")].split(',')[1:]
    return [int(i) for i in str_PR]


def pli_get_valid_chl(row_pli: str) -> list:
    str_pli = row_pli[6:].split(',')
    valid_chl = []
    for idx, item in enumerate(str_pli):
        if item != '100':
            valid_chl.append(idx)
    return valid_chl


def bit_synchro_error_rate(_dir_file: str):
    """ 固定伪距高功率下, CHL PR 各个有效通道对应的值应该差距不大
        如果最大值 - 最小值 大于100, 那么本次释放前的信号一定有比特同步错误
        pop 掉 最异常的值， 再比较 最大值和最小值 的差 ...
        如此循环， 直到剩余的 PR 都是正常的。
        取 ACQ EFF 后面一条 PR。
        分子 = 异常 PR个数
        分母 = 有效 PR个数
    """
    error_PR, total_PR, xujing = 0, 0, 0
    with open(_dir_file, errors="ignore") as fd:
        row_cnt = 0
        get_ACQ_EFF_flag = 0
        valid_chl = []
        for row in fd:
            row_cnt += 1
            if row.startswith("pli a:"):
                pli_row = row
            elif row.startswith("ACQ EFFICIENCY,"):
                ret = re.findall(r'\d+', row)
                chl_total = int(ret[0])
                ir_cnt = int(ret[1])

                if chl_total != 10:
                    valid_chl = pli_get_valid_chl(pli_row)
                else:
                    valid_chl = list(range(10))

                if ir_cnt % 3000 > 2:
                    get_ACQ_EFF_flag = 1
                else:
                    get_ACQ_EFF_flag = 0

            elif row.startswith("CHL PR,"):
                if get_ACQ_EFF_flag:
                    pr_lst = CHL_PR_get_pr(row)
                    valid_pr = []
                    for idx in valid_chl:
                        valid_pr.append(pr_lst[idx])

                    total_PR += len(valid_pr)
                    if len(valid_pr) < 2:
                        print('s')

                    while max(valid_pr) - min(valid_pr) > 100:
                        if max(valid_pr) - min(valid_pr) > 200:
                            print("pr diff {}, row {}".format(max(valid_pr) - min(valid_pr), row_cnt))
                            # print(valid_pr)
                            error_PR += 1
                        else:
                            xujing += 1

                        abnorma_idx = find_the_abnormal_items_idx(valid_pr)
                        valid_pr.pop(abnorma_idx)
                        if len(valid_pr) < 2:
                            break
                    get_ACQ_EFF_flag = 0
                    valid_chl = []

    print("虚警概率 = {:.2%}".format(xujing / total_PR))
    print("bit synchro error rate {} / {} = {:.2%}".format(error_PR, total_PR, error_PR / total_PR))


if __name__ == "__main__":
    fdir = "/home/ucchip/KWQ/gps_test/1205/"
    file_list = [f for f in os.listdir(fdir) if f.endswith('.log') and ("_-115" in f or "_-120" in f or "_-110" in f)]
    file_list.sort()
    for file in file_list:
        print(file)
        bit_synchro_error_rate(fdir + file)
        print()