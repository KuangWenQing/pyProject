#!/usr/bin/env python3
"""
程序名字: file_analysis.py
程序功能: 将 .ubx 文件解析成 .txt 文件
用法: file_analysis.py file_name.ubx
特点: 相比之前写的 C程序(a.out), 没有乱数字, 更快
"""

import os
import sys

up_up_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.append(up_up_dir)

from ubxtranslator.core import Parser
from ubxtranslator.predefined import RXM_CLS


p4 = pow(2, -4)
p21 = pow(2, -21)

if len(sys.argv) == 2:
    path_file = sys.argv[1]
else:
    path_file = "./F9P_log/COM7_210219_074646_F9P.ubx"

parser = Parser([RXM_CLS, ])

fd = open(path_file, 'rb')

while True:
    msg = parser.receive_from(fd)
    if msg == 0:
        break
    elif msg is not None:
        if msg[1] == 'MEASX':
            print('\n', 'numSV =', msg[2][9], ' gpsTOW =', msg[2][1], ' bdsTOW =', msg[2][3])
            print("gnssId  svId    SNR     mpath   doppMS      doppHz      wholeC  fracC   codePhase   intCodePhase "
                  "pseuRangeRMSE")
            for info in msg[2][11]:
                print("{:^8}{:^8}{:^8}{:^8}{:<12.2f}{:<12.2f}{:^8}{:^8}{:^12f}{:^12}{:^12}".format(
                    info[0], info[1], info[2], info[3], info[4] * 0.04, info[5] * 0.2, info[6], info[7],
                    info[8] * p21, info[9], info[10]))
        elif msg[1] == 'RAWX':
            print('\n', 'rcvTow =', msg[2][0], ' week =', msg[2][1], ' leapS =', msg[2][2], ' numMeas =', msg[2][3])
            print("prMes           cpMes           doMes       gnssId  svId  locktime  cno")
            for info in msg[2][6]:
                print("{:<16.2f}{:<16.2f}{:<12.2f}{:^8}{:<8}{:<8}{:^4}".format(
                    info[0], info[1], info[2], info[3], info[4], info[7], info[8]))
            print('----------------------------\n')
