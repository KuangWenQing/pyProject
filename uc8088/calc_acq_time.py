#!/usr/bin/env python3
import sys
import numpy as np


def calc_adjacent_ACQ_SPEC_time(_dir_file_: str)->list:
    ir_list = []
    with open(_dir_file_, 'r') as fd:
        for row in fd:
            if "ACQ SPEC," in row:
                ir = int(row.split("ir")[-1])
                ir_list.append(ir)
    if len(ir_list) < 2:
        return []
    _sub_ir_ = []
    for i in range(1, len(ir_list)):
        temp = ir_list[i] - ir_list[i - 1]
        _sub_ir_.append(temp)
    return _sub_ir_


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: \n"
              "calc_median path_file")
        sys.exit()
    sub_ir = calc_adjacent_ACQ_SPEC_time(sys.argv[1])
    # print(sub_ir)
    if sub_ir:
        print('\033[1;33m' + "ACQ time (median) = {} , (std) = {}".format(np.median(sub_ir),  np.std(sub_ir))
              + '\033[0m')
    else:
        print("ACQ time (median) = 0 , (std) = 0")

