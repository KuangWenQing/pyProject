from ubxTranslate.UBX_RXM import get_epoch_RAWX_from_ubx
from collections import namedtuple
import matplotlib.pyplot as plt
import sys


def analysis_show(dir_path: str, target='pr'):
    """
    前后历元伪距差值的 列表 画图
    """
    try:
        fd = open(dir_path, 'rb')
    except:
        print("open ", path_file, " error")
        sys.exit(-1)

    sv_dict = {}

    for dd in get_epoch_RAWX_from_ubx(fd):
        for key in dd.keys():
            if key in sv_dict.keys():
                sv_dict[key].append(dd[key].prMes)
            else:
                sv_dict[key] = [dd[key].prMes]

    for key in sv_dict.keys():
        k = list(map(lambda x: x[0]-x[1], zip(sv_dict[key][:-1], sv_dict[key][1:])))
        plt.plot(range(len(sv_dict[key])-1), k, marker='*', label=str(key))
        plt.show()


if __name__ == "__main__":
    path_file = r"/home/ucchip/tmp/1210/COM25___115200_211210_062338_save_power.ubx"
    analysis_show(path_file)
