from SIM_Raw import get_epoch_raw_from_simulator
from UBX_Raw import get_raw_word_from_ubx
from threading import Thread
import time

g_sow = 0
g_dd = {}
sv_id = -1
words = []

stop_run = True


def simulate_process(path_file: str):
    global g_dd, g_sow, stop_run
    print('simulate_process star')
    for dd in get_epoch_raw_from_simulator(path_file):
        while stop_run:
            time.sleep(0)
        if stop_run is None:
            return None
        key_list = list(dd.keys())
        g_sow = dd[key_list[0]][1] >> 13
        g_dd = dd
        stop_run = True


def ubx_process(path_file: str):
    global sv_id, words, stop_run
    print('ubx_process star')
    for prn_words in get_raw_word_from_ubx(path_file):
        sv_id, words = prn_words
        if words:
            sow = (words[1] & 0x3fffffff) >> 13
            while sow > g_sow:
                stop_run = False
                time.sleep(0)
            if sow < g_sow:
                continue
            else:
                sim_sv_raw = g_dd[str(sv_id)]
                for i in range(10):
                    if (sim_sv_raw[i] >> 6) != (words[i] & 0x3fffffff) >> 6:
                        print("-"*20)
                        print(sv_id, words)
                        print("sim", sim_sv_raw)
        else:
            stop_run = None
            return None


if __name__ == '__main__':
    path = r"D:\work\temp\1028" + "\\"
    ubx_file = "COM3_211028_042604_M8T.ubx"
    simulator_file = r"中央公园广场.RSIM_(M1B1-GPS_L1)_RawNav(20211028-1225).dat.TXT"

    sim = Thread(target=simulate_process, args=(path + simulator_file, ))
    ubx = Thread(target=ubx_process, args=(path + ubx_file, ))
    sim.start()
    ubx.start()
    sim.join()
    ubx.join()
