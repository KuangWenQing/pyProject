from core import Parser
from predefined import RXM_CLS, NAV_CLS
import sys
GPS_MSG = 0

path_file = r"D:\work\temp\1028\COM3_211028_042604_M8T.ubx"

# f_out = open(r"D:\work\temp\1027\COM3_211027_034801_M8T.txt", 'w')


def get_raw_300bit(dir_file: str):
    try:
        fd = open(dir_file, 'rb')
    except:
        print("open ", dir_file, " error")
        sys.exit(-1)
    parser = Parser([RXM_CLS, NAV_CLS])
    while True:
        msg = parser.receive_from(fd)
        if msg:
            if msg[2].gnssId == GPS_MSG:
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


def get_raw_word_from_ubx(dir_file: str, GNSS_SYS=GPS_MSG):
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
    parser = Parser([RXM_CLS, NAV_CLS])
    while True:
        msg = parser.receive_from(fd)
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
            yield False, False
            sys.exit()


if __name__ == "__main__":
    # for msg in get_raw_word_from_ubx(path + ubx_file):
    #     print(msg)
    for prevlines in get_raw_word_from_ubx(path_file):
        for msg in prevlines:
            print(msg, end='')
        print("---"*30)
