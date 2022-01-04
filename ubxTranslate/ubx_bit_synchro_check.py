from ubxTranslate.UBX_RXM import get_epoch_RAWX_from_ubx
import numpy as np
import logging
import sys

logging.basicConfig(level=logging.DEBUG, format='%(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')


def find_the_abnormal_items_idx(arr: list):
    m = np.median(arr)
    diff_m = []
    for idx, item in enumerate(arr):
        diff_m.append(np.fabs(item - m))
    return diff_m.index(max(diff_m))


def bit_synchro_check(dir_path_: str):
    try:
        fd = open(dir_path_, 'rb')
    except:
        logging.error("\033[1;36m" + "open " + dir_path_ + " error" + "\033[0m")
        sys.exit(-1)

    total_PR, error_PR = 0, 0
    per_sec_pr = []
    for dd in get_epoch_RAWX_from_ubx(fd):
        if dd is None:
            break
        elif len(dd) == 0:
            continue
        for key in dd.keys():
            per_sec_pr.append(dd[key].prMes)
            total_PR += 1
        while max(per_sec_pr) - min(per_sec_pr) > 18:
            error_PR += 1
            abnorma_idx = find_the_abnormal_items_idx(per_sec_pr)
            per_sec_pr.pop(abnorma_idx)
            if len(per_sec_pr) < 2:
                break
        per_sec_pr = []
    print("bit synchro error rate {} / {} = {:.2%}".format(error_PR, total_PR, error_PR / total_PR))


if __name__ == "__main__":
    path_file = r"/home/kwq/work/lab_test/1231/ReceivedTofile-COM3-2021-12-31_15-14-26_pwr144_fixPr.DAT"
    bit_synchro_check(path_file)
