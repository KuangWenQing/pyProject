import os
import re

COM_KEY_NUM = 2
'''kw '''
rep_field_dict = {'ACQ SP': {'ncom': 4, 'hexfmt': [1,1,1,0],
                    'chl':[0,22,8], 'dfn': [0, 17, 5], 'dfs': [0, 12, 5],
                    'sys': [0, 8, 4], 'sv': [0, 2, 6], 'lvl': [0, 0, 2],
                    'dis': [1, 24, 8], 'dsm': [1, 23, 1], 'db': [1, 22, 1],
                    'din': [1, 14, 8], 'nct': [1, 8, 6], 'coh': [1, 3, 5],
                    'dfmc': [1, 1, 2], 'sdis': [2, 16, 16], 'info': [2, 0, 4],
                    'ir': [3, 0, 0]},
                  'acq info': {'ncom': 11, 'hexfmt': [0] * 12,
                    'sv': [0, 0, 0], 'dopp':[1, 0, 0], 'nidle': [2, 0, 0],
                    'dcxo': [3, 0, 0], 'val': [4, 0, 0], 'totcnt': [5, 0, 0],
                    'acqidx GPS': [6, 0, 0], 'acqidx QZS': [7, 0, 0],
                    'acqidx BDS': [8, 0, 0], 'cnlidxH': [9, 0, 0],
                    'cnlidxN': [10, 0, 0], 'sigsyslvl': [11, 0, 0]}}
# rep_file_needs = ['acq pvt', 'acq bb', 'acq fb']
rep_filed_needs = ['ACQ SP', 'acq info']
SIGN_SFIELD = ['dis']
VAL_STR = "0123456789abcdef"
# key_words_list = [rep_field_dict[item]['kw'] for item in rep_file_needs]
def get_int_from_str(line, n, sbl, hex):
    acc_pos = 0
    for it in range(n):
        if sbl in line[acc_pos:]:
            idx_ed = line[acc_pos:].index(sbl)
        else:
            idx_ed = len(line) - 1
        str = ''
        find = False
        for i in range(idx_ed, acc_pos - 1, -1):
            if find and line[i] not in VAL_STR:
                acc_pos += idx_ed
                break
            elif line[i] in VAL_STR:
                str = line[i] + str
                find = True
        if find:
            if hex:
                val = int('0x' + str, 16)
            else:
                val = int(str)
            return val
        else:
            print("WARN! NO VAL FIND!")
            return None

def get_skey_val(skey, val, f_fmt):
    if skey not in SIGN_SFIELD:
        return (val >> f_fmt[1]) & ((1 << f_fmt[2]) - 1)
    else:
        if hex((val >> 24) & ((1 << (f_fmt[2] - 1)))) != '0x0':
            return -1 * (((val ^ 0xffffffff) >> f_fmt[1] & ((1 << f_fmt[2]) - 1)) + 1)
        else:
            return (val >> f_fmt[1]) & ((1 << f_fmt[2]) - 1)

def recons_log_str(line, rep_sfield_dict):
    rep_str = line[:line.index(',') + 1]
    rep_str_list = [key + ' ' + str(rep_sfield_dict[key]) + ',' for key in rep_sfield_dict.keys()]
    for item in rep_str_list:
        rep_str += item
    rep_str += '\n'
    return rep_str

def parse_log(line, key):
    if rep_field_dict[key]['ncom'] != len(re.findall(r',', line)):
        print("UNMATCH COM NUM!")
        return False, None
    nit = len(rep_field_dict[key]['hexfmt'])
    accidx = 0
    rep_sfield_dict = {}
    for it in range(nit):
        if key == 'ACQ SP':
            accidx = accidx + line[accidx:].index(',') + 1
        val = get_int_from_str(line[accidx:], len(rep_field_dict[key]['hexfmt']), ',',
                         rep_field_dict[key]['hexfmt'][0])
        for skey in rep_field_dict[key].keys():
            if skey != 'ncom' and skey != 'hexfmt':
                if rep_field_dict[key][skey][0] == it:
                    if rep_field_dict[key]['hexfmt'][it]:
                        sval = get_skey_val(skey, val, rep_field_dict[key][skey])
                    else:
                        sval = val
                    rep_sfield_dict[skey] = sval
        if key != 'ACQ SP' and it != nit - 1:
            accidx = accidx + line[accidx:].index(',') + 1

    if len(rep_sfield_dict.keys()) != len(rep_field_dict[key].keys()) - COM_KEY_NUM:
        print("ATT! FILED LOSS!")
        return False, None
    else:
        return True, recons_log_str(line, rep_sfield_dict)

def cvt_uart_log(file):
    file_new = file[:-3] + 'rep'
    with open(file_new, 'w') as f_new:
        with open(file, 'r', errors="ignore") as f_ori:
            for line in f_ori:
                tgt_key = None
                for item in rep_filed_needs:
                    if item in line:
                        tgt_key = item
                if not tgt_key:
                    # new_file.write(line.replace(Avengers, Finxters))
                    f_new.write(line)
                else:
                    val, line_new = parse_log(line, tgt_key)
                    try:
                        assert val, 'IN VAL REP! line {}'.format(line)
                    except:
                        print('s')
                    if line_new:
                        f_new.write(line_new)

if __name__ == "__main__":
    # fdir = "/home/htang/gps_test_rec/1021/log0/"

    # fdir = "/home/kwq/work/lab_test/2022/0108/cold_start/"
    fdir = "/home/kwq/work/lab_test/2022/0114/"
    file_list = [f for f in os.listdir(fdir) if f.endswith('.log')]  # and ("-13" in f)]

    # fdir = "/home/ucchip/KWQ/gps_test/1230/"
    # file_list = [f for f in os.listdir(fdir) if f.endswith('.log') and ("3_m" in f)]

    for file in file_list:
        # if os.path.exists(fdir + file[:-3] + "rep"):
        #     continue
        print(file)
        cvt_uart_log(fdir+file)
