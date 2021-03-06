from ubxTranslate.core import Parser
from ubxTranslate.predefined import RXM_CLS, NAV_CLS
import sys
GPS_ID = 0
BDS_ID = 3


path_file = r"/home/kwq/tmp/LG/cmp_m8t_save_pwr/1211-power_save.ubx"
# path_file = r"/home/kwq/tmp/LG/cmp_m8t_save_pwr/1211-continue.ubx"

# path_file = r"/home/kwq/work/lab_test/1102/COM7_211102_101911_F9P.ubx"


# f_out = open(r"D:\work\temp\1027\COM3_211027_034801_M8T.txt", 'w')


def get_raw_300bit(dir_file: str):
    try:
        fd = open(dir_file, 'rb')
    except:
        print("open ", dir_file, " error")
        sys.exit(-1)
    RXM_ID = 0x02
    SFRBX_ID = 0x13
    parser = Parser([RXM_CLS])
    while True:
        msg = parser.receive_from(fd, RXM_ID, SFRBX_ID)
        if msg:
            if msg[2].gnssId == GPS_ID:
                # print(msg, file=f_out)
                svID = "{:<4}".format(msg[2].svId)
                sum_word = 0
                for word in msg[2].RB:
                    # print(word.dwrd, end=' ')
                    sum_word <<= 30
                    sum_word |= (word.dwrd & 0x3fffffff)
                print()
                print(svID, hex(sum_word).upper()[2:])

        elif msg is False:
            sys.exit()


def get_raw_word_from_ubx(dir_file: str, GNSS_SYS=GPS_ID):
    """
    :param dir_file:
    :param GNSS_SYS:
    :return: (scId, [ten words]) ____ every word has 32 bits, both 31 and 32 bit is 1
    """
    try:
        fd = open(dir_file, 'rb')
    except:
        print("open ", dir_file, " error")
        sys.exit(-1)
    RXM_ID = 0x02
    SFRBX_ID = 0x13
    parser = Parser([RXM_CLS])
    while True:
        msg = parser.receive_from(fd, RXM_ID, SFRBX_ID)
        if msg:
            if msg[2].gnssId == GNSS_SYS:
                # print(msg, file=f_out)
                svID = "{}".format(msg[2].svId)
                # sum_word = 0
                word_lst = []
                for word in msg[2].RB:
                    word_lst.append(word.dwrd)
                #     # print(word.dwrd, end=' ')
                #     sum_word <<= 30
                #     sum_word |= (word.dwrd & 0x3fffffff)
                # print()
                # print(svID, hex(sum_word).upper()[2:])
                # yield hex(sum_word).upper()[2:]
                yield svID, word_lst
        elif msg is False:
            fd.close()
            sys.exit()


def get_epoch_RAWX_from_ubx(stream, GNSS_SYS = GPS_ID) -> dict:
    """
    :param file stream:
    :param GNSS_SYS:
    :return: epoch RAWX {svId: information_tuple, }
    """
    RXM_ID = 0x02
    RAWX_ID = 0x15
    parser = Parser([RXM_CLS])
    while True:
        msg = parser.receive_from(stream, RXM_ID, RAWX_ID)
        if msg:
            ret_dd = {}
            for sv_information in msg[2].RB:
                if sv_information.gnssId == GNSS_SYS:
                    ret_dd[sv_information.svId] = sv_information
            yield ret_dd
        elif msg is False:
            return None


def get_epoch_MEASX_from_ubx(stream, GNSS_SYS = GPS_ID) -> dict:
    """
    :param file stream:
    :param GNSS_SYS:
    :return: epoch RAWX {svId: information_tuple, }
    """
    RXM_ID = 0x02
    MEASX_ID = 0x14
    parser = Parser([RXM_CLS])
    while True:
        msg = parser.receive_from(stream, RXM_ID, MEASX_ID)
        if msg:
            ret_dd = {}
            for sv_information in msg[2].RB:
                if sv_information.gnssId == GNSS_SYS:
                    ret_dd[sv_information.svId] = sv_information
            yield ret_dd
        elif msg is False:
            return None


if __name__ == "__main__":
    # path_file = r"/home/kwq/tmp/LG/cmp_m8t_save_pwr/1211-continue.ubx"
    path_file = r"/home/kwq/tmp/LG/cmp_m8t_save_pwr/1211-power_save.ubx"
    try:
        fd = open(path_file, 'rb')
    except:
        print("open ", path_file, " error")
        sys.exit(-1)

    NAV_ID = 0x01
    SVINFO_ID = 0x35
    parser = Parser([NAV_CLS])
    while True:
        msg = parser.receive_from(fd, NAV_ID, SVINFO_ID)
        if msg:
            print(msg[:-1], " == ", msg[-1][:-1])
            for item in msg[-1].RB:
                print(item)
        elif msg is False:
            break

    #
    # for dd in get_epoch_RAWX_from_ubx(fd):
    #     for key in dd.keys():
    #         print(dd[key])
    #     print()
    #
