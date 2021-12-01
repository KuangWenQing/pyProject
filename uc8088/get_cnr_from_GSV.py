import sys, os


def find_first_acq_time_and_first_fix_time(dir_file: str):
    GGA_Flag = "GGA"
    GSV_Flag = "$GPGSV"
    cnr_idx = (7, 11, 15, 19)
    with open(path + file, 'r', errors="ignore") as fd:
        row_cnt = 0
        power_on_flag = 0
        gga = ''
        for row in fd:
            row_cnt += 1
            if GGA_Flag in row:
                gga = row
                if power_on_flag == 0 and "E,1," not in row:
                    power_on_flag = 1
                    print("power on , row cnt =", row_cnt)
                    print(row)
                if power_on_flag == 9 and "E,1," in row:
                    print("first fix row cnt = ", row_cnt)
                    print(gga)
                    # sys.exit(0)
                    return

            if power_on_flag == 1 and GSV_Flag in row:
                if row.count(',') != 19:
                    # print(row_cnt, "row Incomplete ", row)
                    continue
                ret = row[:row.index("*")].split(',')
                for i in cnr_idx:
                    if ret[i]:
                        print(gga)
                        print("first acq row cnt = ", row_cnt)
                        print(row)
                        power_on_flag = 9
                        break


if __name__ == "__main__":
    path = r"D:/Program Files/Serial Port Utility/LOG/1129/"
    # file = "3_TAU1202_hot_start_154.txt"
    file_lst = [f for f in os.listdir(path) if f.endswith('txt')]
    file_lst.sort()
    for file in file_lst:
        print("\n", file)
        find_first_acq_time_and_first_fix_time(path + file)
