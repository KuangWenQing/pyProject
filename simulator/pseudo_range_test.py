"""
use F9P test simulator Signal accuracy
用F9P 测试模拟器 的信号精度
"""

import sys
from collections import deque
from ubxTranslate.UBX_RXM import get_epoch_RAWX_from_ubx
import numpy as np


class ChannelUniformityTest:
    def __init__(self, dir_file):
        self.dir_file = dir_file
        try:
            self.fd = open(dir_file, 'rb')
        except:
            print("open ", dir_file, " error")
            sys.exit(-1)

    def channel_uniformity(self):
        """
        通道一致性测试
        """
        GPS_SYS = 0
        pr_diff_list = []
        for d in get_epoch_RAWX_from_ubx(self.fd, GPS_SYS):
            pr_lst = []
            for k in d.keys():
                pr_lst.append(d[k].prMes)
            pr_diff_list.append(max(pr_lst) - min(pr_lst))
        print("max diff pr = ", max(pr_diff_list))
        print("mean pr diff =", np.mean(pr_diff_list))
        print("std pr diff =", np.std(pr_diff_list))


def pr_ca_accuracy():
    # for two_eph in self.get_2_epoch_target_from_RXM():
    #     old_epoch = two_eph[0]
    #     new_epoch = two_eph[1]
    #     diff_pr
    #     for key in old_epoch.keys():
    pass


if __name__ == "__main__":
    path_file = r"/home/kwq/work/lab_test/1102/COM7_211102_101911_F9P.ubx"

    test = ChannelUniformityTest(path_file)
    test.channel_uniformity()

