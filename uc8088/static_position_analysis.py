import openpyxl
from base_function import write_excel_xlsx
from base_function import analysis_gga
from base_function import xyz_to_lla
from base_function import degree_to_dms
import re
import os
import numpy as np
import matplotlib.pyplot as plt

from base_function import Txyz

T_speed = 0         # 速度 m/s
chart = 1

path = r"D:\temp\1115" + "\\"
path = r"/home/kwq/work/east_window/1211/"
file_list = [f for f in os.listdir(path) if f.endswith('.log')]
# file_list = ['1_lg_211211101225_.txt']

if __name__ == "__main__":
    head_xlsx = [[' ', 'ave', '50%', '95%', 'std', 'cnt']]
    book_name_xlsx = path + 'chart/' + 'speed_and_pos.xlsx'
    # 创建一个workbook对象，而且会在workbook中至少创建一个表worksheet
    wb = openpyxl.Workbook()
    # 获取当前活跃的worksheet,默认就是第一个worksheet
    ws = wb.active
    row_xlsx = 1
    if chart:
        if not os.path.exists(path + 'chart/'):
            os.makedirs(path + 'chart/')
        row_xlsx = write_excel_xlsx(ws, head_xlsx, row_cnt=1)
    fp = open(path + 'chart/abnormal.log', 'w+')
    for file in file_list:
        row_xlsx += 2
        print('\n', file)
        print('\n', file, file=fp)
        all_dis_xyz = []
        if chart:
            row_xlsx = write_excel_xlsx(ws, [[file]], row_xlsx)

        with open(path + file, 'r', errors='ignore') as fd:
            valid_flag = 0
            RMC = ''
            CHL_TIME = ''
            all_xyz = []
            all_diff_xyz = []
            all_ENU = []
            all_EN = []
            all_alt = []
            all_speed = []
            time_lst = []
            for row in fd:
                if "CHL TIME" in row:        # 获取时间, 单位 秒
                    CHL_TIME = row
                    continue

                if ("GPRMC" in row or "GNRMC" in row) and ',A,' in row:
                    valid_flag = 1
                    RMC = row
                    continue
                if (valid_flag and "GPGGA" in row or valid_flag and "GNGGA" in row) and 'KF' not in row and ("E,1," in row or "W,1," in row):
                    if CHL_TIME == '':
                        time = 'no'
                    else:
                        time = int(re.findall(r"\d+", CHL_TIME)[0]) // 1000
                    CHL_TIME = ''

                    sec, lla, xyz, ENU, dis_xyz, dis_en = analysis_gga(Txyz, row)
                    if time == 'no':
                        time = sec
                    if dis_xyz > 1000:
                        print(row, file=fp)

                    all_alt.append(lla[2])  # 收集海拔高
                    all_ENU.append(ENU)  # 收集东北天
                    all_EN.append(ENU[:2])  # 收集东北
                    all_xyz.append(xyz)     # 收集 (x,y,z)
                    diff_xyz = (np.array(Txyz) - np.array(xyz))
                    all_diff_xyz.append(diff_xyz)       # 收集点(x,y,z)3个轴的误差
                    all_dis_xyz.append(dis_xyz)    # 收集点(x,y,z)与真值点Txyz的误差(距离)
                    all_speed.append(float(re.findall(r"\d+\.?\d*", RMC)[3]) * 0.514 - T_speed)
                    time_lst.append(time)
                    valid_flag = 0

            mean_pos_xyz = np.array(all_xyz).mean(axis=0)
            mean_pos_lla = xyz_to_lla(mean_pos_xyz[0], mean_pos_xyz[1], mean_pos_xyz[2])
            Lat = degree_to_dms(str(mean_pos_lla[0]))[0]
            Lon = degree_to_dms(str(mean_pos_lla[1]))[0]
            Alt = round(mean_pos_lla[2], 3)
            print('所有坐标点的均值：', list(mean_pos_xyz), '\n该均值点的经纬高：', Lat, Lon, Alt)
            print('该均值点到真值点的距离 =', round(np.linalg.norm(mean_pos_xyz - np.array(Txyz)), 3), '米')

        for i in range(3):
            if i == 0:
                title = 'X'
            elif i == 1:
                title = 'Y'
            else:
                title = 'Z'
            tmp_lst = [y[i] for y in all_diff_xyz]
            plt.plot(time_lst, tmp_lst, marker='x', label='diff_' + title)
            print('diff_' + title + '  ave =', np.mean(tmp_lst), '  std =', np.std(tmp_lst))
        plt.plot(time_lst, all_dis_xyz, marker='o', label='dis_xyz')
        plt.title("XYZ diff")
        plt.xlabel("SOD (s)")
        plt.ylabel("err (m)")
        plt.legend()  # 不加该语句无法显示 label

        print('dis_xyz ave =', np.mean(all_dis_xyz), '  std =', np.std(all_dis_xyz))
        if chart:
            plt.savefig(path + "chart/" + file[:-4] + "_dis_XYZ.png")

        # plt.figure()
        # plt.title("alt")
        # plt.plot(time_lst, all_alt, marker='x', label='H(m)')
        # plt.legend()  # 不加该语句无法显示 label
        # if chart:
        #     plt.savefig(path + "chart/" + file[:-4] + "_alt.png")

        # plt.figure()
        # plt.title("speed diff")
        # plt.plot(time_lst, all_speed, marker='o', label='v(m/s)')
        # plt.legend()  # 不加该语句无法显示 label
        # if chart:
        #     plt.savefig(path + "chart/" + file[:-4] + "_speed.png")

        plt.figure()
        all_dis_ENU = [np.linalg.norm(enu) for enu in all_ENU]
        all_dis_EN = [np.linalg.norm(en) for en in all_EN]
        plt.title("ENU diff")
        plt.xlabel("SOD (s)")
        plt.ylabel("err (m)")
        plt.plot(time_lst, all_dis_ENU, marker='o', label='ENU')
        plt.plot(time_lst, all_dis_EN, marker='x', label='EN')
        plt.legend()  # 不加该语句无法显示 label
        if chart:
            plt.savefig(path + "chart/" + file[:-4] + "_dis_ENU.png")
        if chart:
            sort_all_dis_xyz = np.sort(all_dis_xyz)
            len_tmp = len(sort_all_dis_xyz)
            dis_xyz_50 = round(sort_all_dis_xyz[int(len_tmp*0.5)], 3)
            dis_xyz_95 = round(sort_all_dis_xyz[int(len_tmp*0.95)], 3)
            dis_xyz_mean = round(np.mean(all_dis_xyz), 3)
            dis_xyz_std = round(np.std(all_dis_xyz), 3)
            dis_xyz_write = ["xyz坐标距离", dis_xyz_mean, dis_xyz_50, dis_xyz_95, dis_xyz_std, len_tmp]
            print("           , mean , cep50 , cep95 , std , cnt")
            print("xyz坐标距离 {:^6}, {:^6}, {:^6}, {:^6}, {: d}".format(dis_xyz_mean,  dis_xyz_50, dis_xyz_95, dis_xyz_std, len_tmp))

            sort_all_dis_ENU = np.sort(all_dis_ENU)
            len_tmp = len(sort_all_dis_ENU)
            dis_ENU_50 = round(sort_all_dis_ENU[int(len_tmp*0.5)], 3)
            dis_ENU_95 = round(sort_all_dis_ENU[int(len_tmp * 0.95)], 3)
            dis_ENU_mean = round(np.mean(all_dis_ENU), 3)
            dis_ENU_std = round(np.std(all_dis_ENU), 3)
            dis_ENU_write = ["东北天", dis_ENU_mean, dis_ENU_50, dis_ENU_95, dis_ENU_std, len_tmp]
            print("东北天      {:^6}, {:^6}, {:^6}, {:^6}, {: d}".format(dis_ENU_mean, dis_ENU_50, dis_ENU_95, dis_ENU_std, len_tmp))

            sort_all_dis_EN = np.sort(all_dis_EN)
            len_tmp = len(sort_all_dis_EN)
            dis_EN_50 = round(sort_all_dis_EN[int(len_tmp * 0.5)], 3)
            dis_EN_95 = round(sort_all_dis_EN[int(len_tmp * 0.95)], 3)
            dis_EN_mean = round(np.mean(all_dis_EN), 3)
            dis_EN_std = round(np.std(all_dis_EN), 3)
            dis_EN_write = ["东北", dis_EN_mean, dis_EN_50, dis_EN_95, dis_EN_std, len_tmp]
            print("东北       {:^6}, {:^6}, {:^6}, {:^6}, {: d}".format(dis_EN_mean, dis_EN_50, dis_EN_95, dis_EN_std, len_tmp))
            plt.figure()
            plt.title("CEP")
            len_tmp = len(sort_all_dis_EN)
            plt.xlabel("err (m)")
            plt.ylabel("per")
            plt.plot(sort_all_dis_EN, [(y+1)/len_tmp for y in range(len_tmp)], marker='x')
            plt.plot(sort_all_dis_EN, [0.95 for y in range(len_tmp)], linestyle="--", label='95%')
            plt.plot(sort_all_dis_EN, [0.50 for y in range(len_tmp)], linestyle="--", label='50%')
            plt.legend()  # 不加该语句无法显示 label
            if chart:
                plt.savefig(path + "chart/" + file[:-4] + "_perc.png")

            sort_all_speed = np.sort(all_speed)
            len_tmp = len(sort_all_speed)
            speed_50 = round(sort_all_speed[int(len_tmp * 0.5)], 3)
            speed_95 = round(sort_all_speed[int(len_tmp * 0.95)], 3)
            speed_mean = round(np.mean(all_speed), 4)
            speed_std = round(np.std(all_speed), 4)
            speed_write = ["speed", speed_mean, speed_50, speed_95, speed_std, len_tmp]
            print("speed     {:^6}, {:^6}, {:^6}, {:^6}, {: d}".format(speed_mean, speed_50, speed_95, speed_std, len_tmp))

            row_xlsx = write_excel_xlsx(ws, [dis_xyz_write, dis_ENU_write, dis_EN_write, speed_write], row_xlsx)
        plt.show()
    fp.close()

