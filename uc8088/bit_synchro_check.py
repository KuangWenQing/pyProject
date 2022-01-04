#!/usr/bin/env python
import os
import sys
# from read_file import ReadFile
import numpy as np
import re

import subprocess as sp
eva_file = '/home/ucchip/Desktop/tmp_file/_tmp_pr.txt'
BSYN_ERR_THRE = 3e5 - 500
FSYN_PR_THRE = 6e6
TRK_AB_THRE = 1e2
BIT_STUCK_THRE = 16
# true_pr_threshold = 2e7


# def del_ab_val_calc_mean(arr: list):
#     """
#     ram arr:  an array
#     :return:  the mean of arr without the abnormal items
#     """
#     if len(arr) < 3:
#         return np.mean(arr)
#     max_val = max(arr)
#     min_val = min(arr)
#
#     max_idx = arr.index(max_val)
#     min_idx = arr.index(min_val)
#
#     del_max = arr.copy()
#     del_max.pop(max_idx)
#     del_min = arr.copy()
#     del_min.pop(min_idx)
#
#     del_max_std = np.std(del_max)
#     del_min_std = np.std(del_min)
#
#     if del_max_std < del_min_std:
#         diff_ = np.fabs(max_val - np.mean(del_max))
#         if diff_ > 100:
#             return del_ab_val_calc_mean(del_max)
#         else:
#             return np.mean(arr)
#     else:
#         diff_ = np.fabs(min_val - np.mean(del_min))
#         if diff_ > 100:
#             return del_ab_val_calc_mean(del_min)
#         else:
#             return np.mean(arr)


def split_pli(s: str):
    try:
        s = s[s.index('a:')+3:]
    except:
        print("s")
    return s.split(',')


def split_PR(s: str):
    if 'ir' in s:
        s = s[:s.index("ir")]
    else:
        return None
    return s.split(',')[1:]


def get_valid_chl(s: str):
    valid_chl = []
    pli_list = split_pli(s)
    for idx, item in enumerate(pli_list):
        try:
            if int(item) != 100:
                valid_chl.append(idx)
        except:
            print("stop")
    return valid_chl


def get_pr_list(s: str):
    pr_list = []
    pr_str_list = split_PR(s)
    for i in pr_str_list:
        pr_list.append(int(i))
    return pr_list


# def get_valid_pr_dict(pli: str, pr: str):
#     valid_chl = get_valid_chl(pli)
#     pr_list = get_pr_list(pr)
#     valid_pr_dict = {}
#     for chl in valid_chl:
#         valid_pr_dict[chl] = pr_list[chl]
#     return valid_pr_dict


# def arr_check


# def bit_synchro_check(pli: str, pr: str):
#     error = 0
#     valid_pr_dict = get_valid_pr_dict(pli, pr)
#     if len(valid_pr_dict) < 3:
#         return error
#
#     frame_chl_pr_dict = {}
#     bit_lock_chl = []
#     for key in valid_pr_dict:
#         if valid_pr_dict[key] > true_pr_threshold:
#             frame_chl_pr_dict[key] = valid_pr_dict[key]
#         else:
#             bit_lock_chl.append(key)
#
#     for


def get_bit_syn_chl(pr_lst_val, chl_lst, dpr_thre):
    pr_lst_bak = pr_lst_val.copy()
    chl_lst_bak = chl_lst.copy()
    ab_chl = []
    while 1:
        if len(pr_lst_bak) < 3 and ab_chl:
            ab_chl.clear()
            return False, ab_chl
        pr_mean = np.median(pr_lst_bak)
        dpr_lst = [np.abs(item - pr_mean) for item in pr_lst_bak]
        idx = np.argmax(dpr_lst)
        if max(dpr_lst) < dpr_thre:
            break
        else:
            ab_chl.append(chl_lst_bak[idx])
            chl_lst_bak.pop(idx)
            pr_lst_bak.pop(idx)
    return True, ab_chl

def get_fync_chl(pr_lst_val, chl_lst):
    fsyn_chl, fsyn_pr = [], []
    for idx, pr in enumerate(pr_lst_val):
        if pr > FSYN_PR_THRE:
            fsyn_chl.append(chl_lst[idx])
            fsyn_pr.append(pr_lst_val[idx])

    return fsyn_pr, fsyn_chl

def bit_syn_cnt_renew(bit_syn_cnt, chl_lst):
    cnt_renew = bit_syn_cnt.copy()
    for chl in chl_lst:
        cnt_renew[chl] += 1
    return cnt_renew

def bit_syn_stuck_judge(bit_syn_cnt, fsyn_chl):
    chl = []
    for idx, cnt in enumerate(bit_syn_cnt):
        if cnt > BIT_STUCK_THRE and idx not in fsyn_chl:
            chl.append(idx)
    return chl

def rm_bit_err_chl(bit_err_chl_lst, fsyn_chl_lst, fsyn_pr_lst):
    chl_renew, pr_renew = [], []
    for idx, chl in enumerate(fsyn_chl_lst):
        if chl not in bit_err_chl_lst:
            chl_renew.append(chl)
            pr_renew.append(fsyn_pr_lst[idx])
    return chl_renew, pr_renew

def extract_tgt(fpath):
    # sp.check_output("grep -an 'ACQ EFFICIENCY,\|FREE ALL\|CHL PR,\|pli a:' {} > {} ".format(fpath, eva_file), shell=True)
    sp.check_output("grep -an 'FREE ALL\|CHL PR,\|pli a:' {} > {} ".format(fpath, eva_file), shell=True)

def eva_bit_syn_err():
    fd_ab = open("/home/ucchip/KWQ/gps_test/1013/trk_ab.txt", 'w')
    fd_bitsyn = open("/home/ucchip/KWQ/gps_test/1013/bit_syn_ab.txt", 'w')
    fd_stuck = open("/home/ucchip/KWQ/gps_test/1013/bit_stuck_ab.txt", 'w')
    free, pli_val, pr_val = False, False, False
    bit_syn_err, eva_bit_stuck_chl = [], []
    chl_lst = []
    pli_lst_val, pr_lst_val = None, None
    bit_syn_cnt = [0] * 10
    high_power_time_span = 200     # 高功率判决标准 时间跨度(中断数)
    back_ir, now_ir = 0, 0         # 上一个历元 、 当前历元 的中断计数器的值
    with open(eva_file, 'r', errors="ignore") as fd:
        for cont in fd:
            rowidx = int(cont.split(':')[0])
            if pli_val and pr_val:
                pr_lst_val = [pr_lst[item] for item in chl_lst]
                bit_syn_cnt = bit_syn_cnt_renew(bit_syn_cnt, chl_lst)
            if 'pli' in cont:
                chl_lst = get_valid_chl(cont)
                pli_val = True
            elif chl_lst and len(chl_lst) > 3 and pli_val and 'CHL PR' in cont:
                try:
                    pr_lst = get_pr_list(cont)
                except:
                    pass
                    # print(cont)
                    # print('s')
                pr_val = True
            elif 'FREE ALL' in cont:
                '''tp '''
                bit_err_chl_lst, trk_ab_chl_lst = [], []
                if not pr_lst_val:
                    continue
                fsyn_pr_lst, fsyn_chl_lst = get_fync_chl(pr_lst_val, chl_lst)
                if len(fsyn_pr_lst) < 3:
                    print("ATT! NO ENOUGH FSYN CHL, row{}".format(rowidx))
                else:
                    val, bit_err_chl_lst = get_bit_syn_chl(fsyn_pr_lst, fsyn_chl_lst, BSYN_ERR_THRE)
                    if not val:
                        print("CAN NOT FIND BIT SYN ERR CHL", file=fd_bitsyn)
                    else:
                        print("BIT SYN ERR CHL {}, row {}".format(bit_err_chl_lst, rowidx), file=fd_bitsyn)
                        print("ORI PR {}",  pr_lst, file=fd_bitsyn)
                        # print("ORI CHL {}", fsyn_chl_lst, file=fd_bitsyn)
                        print("", file=fd_bitsyn)
                    if bit_err_chl_lst:
                        rm_berr_chl_lst, rm_berr_pr_lst = rm_bit_err_chl(bit_err_chl_lst, fsyn_chl_lst, fsyn_pr_lst)
                    else:
                        rm_berr_chl_lst = fsyn_chl_lst.copy()
                        rm_berr_pr_lst = fsyn_pr_lst.copy()
                    val, trk_ab_chl_lst = get_bit_syn_chl(rm_berr_pr_lst, rm_berr_chl_lst, TRK_AB_THRE)
                    if not val:
                        print("CAN NOT FIND BIT SYN ERR CHL", file=fd_ab)
                    else:
                        print("TRK AB CHL {}, row {}".format(trk_ab_chl_lst, rowidx), file=fd_ab)
                # if len(bit_err_chl_lst):
                #     print('s')
                bit_syn_err.append([rowidx, len(fsyn_pr_lst), len(bit_err_chl_lst), len(trk_ab_chl_lst)])
                bit_stuck_chl = bit_syn_stuck_judge(bit_syn_cnt, fsyn_chl_lst)
                if bit_stuck_chl:
                    bit_syn_cnt_arr = np.array(bit_syn_cnt)
                    print("BIT STUCK CHL {}, cnt {}, row {}".format(bit_stuck_chl, bit_syn_cnt_arr[bit_stuck_chl], rowidx), file=fd_stuck)
                    eva_bit_stuck_chl.append(len(bit_stuck_chl))
                pli_val, pr_val = False, False
                bit_syn_cnt = [0] * 10
                pr_lst_val.clear()
            # elif cont.startswith("ACQ"):
            #     nfsyn_ircnt = re.findall(r"\d+", cont)
            #     assert len(nfsyn_ircnt) == 2
            #     nfsyn, now_ir = int(nfsyn_ircnt[0]), int(nfsyn_ircnt[1])
            #     if (now_ir - back_ir < high_power_time_span) and nfsyn == 10:
            #         pass




    '''sum bit-syn err rate'''
    sum_fsyn, sum_bit_err, sum_trk_err = 0, 0, 0
    for item in bit_syn_err:
        sum_fsyn += item[1]
        sum_bit_err += item[2]
        sum_trk_err += item[3]
    if sum_fsyn:
        print("bit syn rate {}, val statis num {}".format(sum_bit_err/sum_fsyn, sum_fsyn))
        print("trk err rate {}, val statis num {}".format(sum_trk_err / sum_fsyn, sum_fsyn))
        print("bit stuck rate {}, val statis num {}".format(sum(eva_bit_stuck_chl) / sum_fsyn, sum_fsyn))
    else:
        print("sum_fsyn = 0")

    fd_ab.close()
    fd_bitsyn.close()
    fd_stuck.close()
# if __name__ == "__main__":
#     ReadFile.number_of_parameters(2)
#     path = sys.argv[1]
#     if not path.endswith('/'):
#         path += '/'
#     file = sys.argv[2]
#
#     print("path: %s/" % path)
#     print("file: %s" % file)
#
#     fd = ReadFile(path, file)
#
#     while fd.pos < fd.FILE_LEN:
#         ret = fd.extract_target_row()
#         print(ret)

if __name__ == "__main__":
    # fpath = "/home/ucchip/KWQ/gps_test/1013/7_acqThre_nct18coh9_-144_gps_dopp10_5_0_4_para83_69_42_22_0_22_12_1_10_51_bin211013101727_RXSC63.log"
    #fpath = "/home/ucchip/KWQ/gps_test/1013/8_acqThre_nct18coh9_-144_gps_dopp10_5_0_4_para83_69_42_22_0_22_12_1_10_51_bin211013101727_RXSC40.log"
    #fpath = "/home/ucchip/th/gps_test_rec/1014/4_acqThre_nct18coh9_-144_gps_dopp10_5_0_4_para83_69_42_22_0_22_12_1_10_51_1063918.log"
    #fpath = "/home/ucchip/KWQ/gps_test/1015/2_mdlTCXO_acqThre_nct18coh9_-144_gps_dopp10_5_0_4_para83_69_42_22_0_22_12_1_10_51_963918_rxsc40.log"
    # fpath = "/home/ucchip/KWQ/gps_test/1015/1_mdl2_acqThre_nct18coh9_-144_gps_dopp10_5_0_4_para83_69_42_22_0_22_12_1_10_51_1053918_rxsc40.log"
    #fpath = "/home/ucchip/KWQ/gps_test/1015/12_mdlTCXO_acqThre_nct26coh9_-147_gps_dopp10_5_0_4_para83_69_42_22_0_22_12_1_10_51_1153918_rxsc40.log"
    #fpath = "/home/ucchip/KWQ/gps_test/1015/13_mdlTCXO_acqThre_nct18+coh9_-147_gps_dopp10_5_0_4_para83_69_42_22_0_22_12_1_10_51_1153918_rxsc0.log"
    #fpath = "/home/ucchip/KWQ/gps_test/1021/1_mdlTCXO_acqThre_nct18coh9_-144_gps_dopp10_5_0_7_para83_69_42_22_0_22_12_1_10_51_1153918_rxsc40.log"
    # extract_tgt(fpath)
    # eva_bit_syn_err()

    fdir = "/home/ucchip/KWQ/gps_test/1223/"
    file_list = [f for f in os.listdir(fdir) if f.endswith('.rep') and "-13" in f]  # and ("-13" in f or "-125" in f) and f.startswith("2")]
    # file_list = ["20_mdl_new8_acqThre_nct26coh9_-143_gps_dopp10_10_0_0_para83_69_42_22_0_19_12_1_10_32_1163918_rxsc16_SLVL3.log"]
    file_list.sort()
    for file in file_list:
        print(fdir + file)
        extract_tgt(fdir + file)
        eva_bit_syn_err()
        print()


