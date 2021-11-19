import os


def parsing_RANGEA(line: str) -> dict:
    sv_info = {}
    # print(line)
    if ";" in line:
        dislodge_head = line.split(';')[1]
        if '*' in dislodge_head:
            dislodge_crc = dislodge_head.split('*')[0]
            # print(dislodge_crc)
            ret = dislodge_crc.split(',')
            num_obs = int(ret.pop(0))  # 第一个字段是 obs Number

            for i in range(num_obs):
                try:
                    sv_id = ret[10 * i]
                    cnr = ret[10 * i + 7]
                    ch_tr_status = ret[10 * i + 9]
                except:
                    break
                dec_ = int(ch_tr_status, 16)

                # 如果是 北斗系统
                if (dec_ & 0x70000) >> 16 == 4:
                    # print('sv%s,   %s' % (sv_id, ch_tr_status))
                    fre_filed = (dec_ & 0x3e00000) >> 21
                    if fre_filed == 8 or fre_filed == 23:
                        if sv_id in sv_info.keys():
                            continue
                        else:
                            sv_info[sv_id] = cnr
    return sv_info


# 116 <=> 45.5,   121 <=> 40.5 , 126 <=> 35.5,  131 <=> 30.4 ,  133 <=> 28.1
dd_power = {
    "116": "#RANGEA,COM1,0,98.0,FINE,1809,92954.000,960110,1,16;18,6,0,38267951.994,0.047,-199271268.543345,0.005,-1629.355,47.1,322.020,281c1c24,7,0,35870837.239,0.047,-186788867.544427,0.005,-156.739,47.1,298.020,281c1c44,9,0,37354251.868,0.047,-194513393.045015,0.005,802.421,47.1,322.020,281c1c64,10,0,35885078.125,0.047,-186863018.377679,0.005,-85.679,47.1,298.020,281c1c84,15,0,24570187.718,0.047,-127943417.331524,0.005,-371.762,47.1,298.020,281c1ca4,16,0,24639583.706,0.047,-128304778.166688,0.005,-2567.160,47.1,322.020,281c1ce4,22,0,23190240.057,0.047,-120757666.166308,0.005,1788.105,47.1,298.020,281c1de4,22,0,23190243.007,0.062,-121865549.737681,0.006,1804.475,45.2,281.020,211c1de0,23,0,21903356.894,0.047,-114056531.795298,0.005,-493.579,47.1,298.020,281c1e04,23,0,21903359.407,0.063,-115102930.144502,0.006,-498.099,45.1,281.020,211c1e00,29,0,24580978.866,0.047,-127999611.867633,0.005,3260.172,47.2,298.020,281c1e24,29,0,24580982.498,0.063,-129173936.569039,0.006,3290.120,45.2,281.020,211c1e20,30,0,23027552.905,0.047,-119910513.508097,0.005,1113.725,47.1,298.020,281c1e44,30,0,23027555.748,0.063,-121010622.942655,0.006,1123.976,45.1,281.020,211c1e40,24,0,24807446.737,0.047,-129178885.218434,0.005,-2243.451,47.1,322.020,281c1ec4,24,0,24807449.554,0.063,-130364025.976251,0.006,-2263.971,45.2,317.020,211c1ec0,31,0,24898053.210,0.047,-129650699.161549,0.005,-1761.901,47.1,322.020,281c1ee4,31,0,24898055.972,0.063,-130840168.203889,0.006,-1778.044,45.2,317.020,211c1ee0*25f28fe2",
    "121": "#RANGEA,COM1,0,98.0,FINE,1809,93203.000,1209109,1,16;18,6,0,38346403.260,0.046,-199679784.241927,0.005,-1651.111,47.2,571.020,281c1c24,7,0,35878384.486,0.046,-186828167.878925,0.005,-158.117,47.2,547.020,281c1c44,9,0,37316594.127,0.046,-194317299.705168,0.005,773.234,47.2,571.020,281c1c64,10,0,35889879.293,0.047,-186888019.409443,0.005,-114.615,47.2,547.020,281c1c84,15,0,24591086.556,0.047,-128052242.818448,0.005,-501.430,47.2,547.020,281c1ca4,16,0,24763618.785,0.047,-128950660.655921,0.005,-2619.090,47.1,571.020,281c1ce4,22,0,23105545.491,0.047,-120316639.568361,0.005,1754.810,47.2,547.020,281c1de4,22,0,23105548.349,0.061,-121420477.617364,0.006,1770.956,45.4,530.020,211c1de0,23,0,21928232.748,0.047,-114186066.688751,0.005,-546.255,47.2,547.020,281c1e04,23,0,21928235.189,0.061,-115233653.663492,0.006,-551.250,45.4,530.020,211c1e00,29,0,24425942.348,0.047,-127192297.139645,0.005,3223.897,47.1,547.020,281c1e24,29,0,24425945.896,0.061,-128359215.977435,0.006,3253.547,45.4,530.020,211c1e20,30,0,22977564.436,0.047,-119650210.437959,0.005,977.277,47.2,547.020,281c1e44,30,0,22977567.192,0.061,-120747932.054244,0.006,986.215,45.4,530.020,211c1e40,24,0,24915224.059,0.046,-129740109.747142,0.005,-2263.726,47.2,571.020,281c1ec4,24,0,24915226.836,0.060,-130930399.414248,0.006,-2284.460,45.5,566.020,211c1ec0,31,0,24985148.137,0.046,-130104224.704956,0.005,-1879.555,47.2,571.020,281c1ee4,31,0,24985150.698,0.100,-131297854.910671,0.009,-1896.760,40.5,566.020,211c1ee0*69115d89",
    "126": "#RANGEA,COM1,0,98.0,FINE,1809,93683.000,1689107,1,16;18,6,0,38500590.615,0.047,-200482677.773287,0.005,-1694.995,47.2,1051.020,281c1c24,7,0,35893164.923,0.047,-186905133.661493,0.005,-163.500,47.1,1027.020,281c1c44,9,0,37248030.314,0.047,-193960270.084992,0.005,713.210,47.2,1051.020,281c1c64,10,0,35903241.147,0.047,-186957597.904655,0.005,-177.162,47.1,1027.020,281c1c84,15,0,24648761.843,0.047,-128352572.758106,0.005,-749.861,47.2,1027.020,281c1ca4,16,0,25009225.325,0.047,-130229596.828617,0.005,-2707.575,47.1,1051.020,281c1ce4,22,0,22946967.734,0.047,-119490884.138544,0.005,1683.974,47.2,1027.020,281c1de4,22,0,22946970.560,0.061,-120587147.370158,0.006,1699.459,45.4,1010.020,211c1de0,23,0,21983447.669,0.046,-114473585.305778,0.005,-653.217,47.2,1027.020,281c1e04,23,0,21983450.108,0.061,-115523810.449617,0.006,-659.227,45.4,1010.020,211c1e00,29,0,24132722.917,0.047,-125665428.536211,0.005,3133.103,47.1,1027.020,281c1e24,29,0,24132726.208,0.061,-126818340.646532,0.006,3161.896,45.4,1010.020,211c1e20,30,0,22900021.313,0.047,-119246423.459396,0.005,702.425,47.1,1027.020,281c1e44,30,0,22900023.966,0.061,-120340441.080297,0.006,708.895,45.4,1010.020,211c1e40,24,0,25125849.688,0.046,-130836891.219743,0.005,-2307.488,47.2,1051.020,281c1ec4,24,0,25125852.354,0.061,-132037243.348176,0.006,-2328.679,45.4,1046.020,211c1ec0,31,0,25168625.577,0.047,-131059639.667762,0.005,-2100.176,47.2,1051.020,281c1ee4,31,0,25168628.107,0.150,-132262035.953580,0.013,-2119.355,35.5,1046.020,211c1ee0*49308d27",
    "131": "#RANGEA,COM1,0,98.0,FINE,1809,93946.000,1952106,1,16;18,6,0,38586750.943,0.046,-200931336.845745,0.005,-1715.326,47.3,1314.020,281c1c24,7,0,35901457.322,0.046,-186948314.210801,0.005,-163.425,47.3,1290.020,281c1c44,9,0,37212807.694,0.046,-193776856.788357,0.005,682.998,47.3,1314.020,281c1c64,10,0,35913063.514,0.046,-187008745.779822,0.005,-210.588,47.2,1290.020,281c1c84,15,0,24689962.376,0.046,-128567114.559997,0.005,-879.762,47.3,1290.020,281c1ca4,16,0,25146983.296,0.046,-130946937.628611,0.005,-2745.042,47.3,1314.020,281c1ce4,22,0,22862907.237,0.046,-119053159.366035,0.005,1645.892,47.3,1290.020,281c1de4,22,0,22862909.992,0.062,-120145407.202356,0.006,1661.032,45.3,1273.020,211c1de0,23,0,22017912.765,0.046,-114653053.760306,0.005,-710.279,47.3,1290.020,281c1e04,23,0,22017915.092,0.062,-115704925.569130,0.006,-716.746,45.3,1273.020,211c1e00,29,0,23975923.518,0.046,-124848933.618663,0.005,3076.282,47.3,1290.020,281c1e24,29,0,23975926.684,0.061,-125994355.561613,0.006,3104.526,45.3,1273.020,211c1e20,30,0,22868402.753,0.046,-119081777.551243,0.005,550.675,47.3,1290.020,281c1e44,30,0,22868405.424,0.062,-120174284.934711,0.006,555.720,45.3,1273.020,211c1e40,24,0,25242981.276,0.046,-131446825.728530,0.005,-2329.393,47.3,1314.020,281c1ec4,24,0,25242983.971,0.061,-132652773.743973,0.006,-2350.751,45.3,1309.020,211c1ec0,31,0,25277585.943,0.046,-131627024.392440,0.005,-2212.391,47.3,1314.020,281c1ee4,31,0,25277588.403,0.211,-132834626.545236,0.018,-2232.529,30.4,1309.020,211c1ee0*d4153dbf",
    "136": "#RANGEA,COM1,0,99.0,FINE,1809,94567.000,2573104,1,16;17,6,0,38793400.028,0.044,-202007411.818989,0.005,-1747.419,47.5,1935.020,281c1c24,7,0,35920250.129,0.043,-187046173.363946,0.005,-149.428,47.6,1911.020,281c1c44,9,0,37134970.856,0.044,-193371540.129128,0.005,624.632,47.5,1935.020,281c1c64,10,0,35942472.429,0.043,-187161885.192963,0.005,-281.620,47.6,1911.020,281c1c84,15,0,24811991.561,0.043,-129202551.941992,0.005,-1161.496,47.6,1911.020,281c1ca4,16,0,25477889.859,0.044,-132670052.806215,0.005,-2796.787,47.5,1935.020,281c1ce4,22,0,22671621.564,0.043,-118057085.143086,0.005,1562.753,47.6,1911.020,281c1de4,22,0,22671624.178,0.064,-119140195.448846,0.006,1577.036,45.1,1894.020,211c1de0,23,0,22110157.399,0.044,-115133395.716486,0.005,-835.393,47.5,1911.020,281c1e04,23,0,22110159.687,0.063,-116189674.691206,0.006,-843.080,45.1,1894.020,211c1e00,29,0,23617650.298,0.043,-122983312.816751,0.005,2928.016,47.6,1911.020,281c1e24,29,0,23617653.251,0.063,-124111620.216054,0.006,2954.928,45.1,1894.020,211c1e20,30,0,22823829.415,0.044,-118849672.681704,0.005,197.518,47.5,1911.020,281c1e44,30,0,22823831.911,0.063,-119940051.209016,0.006,199.312,45.1,1894.020,211c1e40,24,0,25523301.806,0.044,-132906526.343463,0.005,-2369.952,47.5,1935.020,281c1ec4,24,0,25523304.435,0.063,-134125866.468607,0.006,-2391.655,45.1,1930.020,211c1ec0,31,0,25555780.398,0.043,-133075655.203902,0.005,-2446.581,47.6,1935.020,281c1ee4*7c536006",
    "132": "#RANGEA,COM1,0,99.0,FINE,1809,94798.000,2804103,1,16;18,6,0,38871274.041,0.046,-202412921.533131,0.005,-1762.991,47.2,2166.020,281c1c24,7,0,35926875.639,0.047,-187080674.180142,0.005,-148.841,47.2,2142.020,281c1c44,9,0,37107856.726,0.046,-193230349.991817,0.005,598.247,47.2,2166.020,281c1c64,10,0,35955700.128,0.047,-187230765.689242,0.005,-314.477,47.1,2142.020,281c1c84,15,0,24865854.241,0.047,-129483028.542457,0.005,-1265.953,47.2,2142.020,281c1ca4,16,0,25602331.757,0.047,-133318053.378652,0.005,-2812.414,47.2,2166.020,281c1ce4,22,0,22603148.054,0.047,-117700526.043002,0.005,1524.541,47.2,2142.020,281c1de4,22,0,22603150.607,0.065,-118780365.383048,0.007,1538.591,44.9,2125.020,211c1de0,23,0,22148391.167,0.046,-115332489.061677,0.005,-888.022,47.2,2142.020,281c1e04,23,0,22148393.497,0.065,-116390594.702365,0.007,-896.147,44.9,2125.020,211c1e00,29,0,23489290.916,0.046,-122314912.600818,0.005,2858.539,47.2,2142.020,281c1e24,29,0,23489293.794,0.065,-123437088.309499,0.007,2884.800,44.9,2125.020,211c1e20,30,0,22818135.733,0.046,-118820024.283741,0.005,59.496,47.2,2142.020,281c1e44,30,0,22818138.191,0.065,-119910131.011253,0.007,60.052,44.9,2125.020,211c1e40,24,0,25628897.080,0.047,-133456387.816338,0.005,-2390.367,47.2,2166.020,281c1ec4,24,0,25628899.673,0.065,-134680772.673602,0.007,-2412.284,44.9,2161.020,211c1ec0,31,0,25666225.378,0.046,-133650771.000371,0.005,-2531.704,47.2,2166.020,281c1ee4,31,0,25666227.548,0.341,-134876933.611374,0.028,-2554.990,29.0,73.020,211c1ee0*ca57fbe0",
    "133": "#RANGEA,COM1,0,99.0,FINE,1809,94942.000,2948103,1,16;18,6,0,38920253.234,0.044,-202667968.685963,0.005,-1774.669,47.5,2310.020,281c1c24,7,0,35931081.593,0.044,-187102575.504988,0.005,-150.732,47.5,2286.020,281c1c44,9,0,37091635.655,0.044,-193145882.599670,0.005,579.556,47.5,2310.020,281c1c64,10,0,35964782.601,0.044,-187278060.450191,0.005,-337.760,47.5,2286.020,281c1c84,15,0,24901842.109,0.044,-129670426.571732,0.005,-1331.872,47.4,2286.020,281c1ca4,16,0,25680309.376,0.044,-133724102.490723,0.005,-2822.193,47.5,2310.020,281c1ce4,22,0,22561421.531,0.044,-117483245.396820,0.005,1497.793,47.5,2286.020,281c1de4,22,0,22561424.068,0.065,-118561091.483235,0.007,1511.574,44.9,2269.020,211c1de0,23,0,22173503.236,0.044,-115463254.019407,0.005,-923.469,47.4,2286.020,281c1e04,23,0,22173505.474,0.065,-116522559.416557,0.007,-931.919,44.9,2269.020,211c1e00,29,0,23410967.425,0.044,-121907061.847849,0.005,2810.362,47.5,2286.020,281c1e24,29,0,23410970.232,0.065,-123025496.042790,0.007,2836.203,44.9,2269.020,211c1e20,30,0,22817779.573,0.044,-118818169.620984,0.005,-29.110,47.5,2286.020,281c1e44,30,0,22817781.997,0.065,-119908259.452220,0.007,-29.309,44.9,2269.020,211c1e40,24,0,25695274.470,0.044,-133802031.998107,0.005,-2405.594,47.5,2310.020,281c1ec4,24,0,25695277.085,0.065,-135029587.945568,0.007,-2427.576,44.9,2305.020,211c1ec0,31,0,25737043.582,0.044,-134019539.949757,0.005,-2585.190,47.5,2310.020,281c1ee4,31,0,25737045.366,0.576,-135249086.188267,0.048,-2609.501,28.0,1.020,011c1ee0*5b780367",
    "134": "#RANGEA,COM1,0,99.0,FINE,1809,95103.000,3109105,2,16;17,6,0,38975205.723,0.045,-202954120.447545,0.005,-1774.083,47.4,2471.020,281c1c24,7,0,35935658.199,0.045,-187126407.052293,0.005,-139.481,47.4,2447.020,281c1c44,9,0,37073923.619,0.045,-193053651.504565,0.005,572.059,47.4,2471.020,281c1c64,10,0,35975518.451,0.045,-187333964.659258,0.005,-350.863,47.4,2447.020,281c1c84,15,0,24944028.480,0.045,-129890101.890212,0.005,-1390.797,47.4,2447.020,281c1ca4,16,0,25767594.950,0.045,-134178620.881404,0.005,-2817.732,47.3,2471.020,281c1ce4,22,0,22515469.496,0.045,-117243960.995313,0.005,1480.424,47.4,2447.020,281c1de4,22,0,22515471.980,0.063,-118319611.951094,0.006,1494.074,45.1,2430.020,211c1de0,23,0,22202560.069,0.045,-115614560.715403,0.005,-950.235,47.4,2447.020,281c1e04,23,0,22202562.349,0.063,-116675254.330255,0.006,-958.927,45.2,2430.020,211c1e00,29,0,23324822.889,0.045,-121458484.930762,0.005,2767.493,47.4,2447.020,281c1e24,29,0,23324825.573,0.063,-122572803.998665,0.006,2792.878,45.2,2430.020,211c1e20,30,0,22820098.423,0.045,-118830244.448919,0.005,-115.043,47.4,2447.020,281c1e44,30,0,22820100.798,0.063,-119920445.184738,0.006,-116.034,45.2,2430.020,211c1e40,24,0,25769800.886,0.045,-134190110.150078,0.005,-2409.403,47.4,2471.020,281c1ec4,24,0,25769803.520,0.063,-135421226.582288,0.006,-2431.534,45.1,2466.020,211c1ec0,31,0,25817759.281,0.045,-134439847.344668,0.005,-2629.828,47.4,2471.020,281c1ee4*654d7676",
    "133": "#RANGEA,COM1,0,99.0,FINE,1809,95585.000,3591101,1,16;18,6,0,39141066.373,0.046,-203817799.302635,0.005,-1796.518,47.3,2953.020,281c1c24,7,0,35948796.145,0.045,-187194819.863661,0.005,-131.723,47.3,2929.020,281c1c44,9,0,37023790.623,0.045,-192792596.117775,0.005,523.965,47.3,2953.020,281c1c64,10,0,36011689.354,0.046,-187522316.107822,0.005,-418.599,47.3,2929.020,281c1c84,15,0,25082385.584,0.046,-130610562.849236,0.005,-1583.413,47.3,2929.020,281c1ca4,16,0,26029143.552,0.046,-135540570.496942,0.005,-2817.667,47.3,2953.020,281c1ce4,22,0,22382777.436,0.046,-116552998.991252,0.005,1398.077,47.3,2929.020,281c1de4,22,0,22382779.808,0.063,-117622311.254600,0.006,1411.000,45.2,2912.020,211c1de0,23,0,22296083.860,0.046,-116101563.171697,0.005,-1058.454,47.3,2929.020,281c1e04,23,0,22296086.087,0.063,-117166724.948112,0.006,-1068.115,45.1,2912.020,211c1e00,29,0,23076883.649,0.046,-120167401.464010,0.005,2598.784,47.3,2929.020,281c1e24,29,0,23076886.249,0.062,-121269876.413178,0.006,2622.744,45.2,2912.020,211c1e20,30,0,22844440.736,0.045,-118957001.418399,0.005,-398.119,47.4,2929.020,281c1e44,30,0,22844443.075,0.063,-120048365.480771,0.006,-401.745,45.1,2912.020,211c1e40,24,0,25995168.434,0.046,-135363652.237589,0.005,-2447.615,47.3,2953.020,281c1ec4,24,0,25995170.691,0.063,-136605537.266417,0.006,-2470.007,45.2,2948.020,211c1ec0,31,0,26068773.037,0.046,-135746941.380416,0.005,-2778.263,47.3,2953.020,281c1ee4,31,0,26068774.540,0.477,-136992335.404092,0.040,-2804.082,28.1,32.020,211c1ee0*081b021f"
}


if __name__ == "__main__":
    path = "D:\\work\\0701\\"
    # file_lst = [f for f in os.listdir(path) if f.endswith('log')]
    file_lst = ["11.log"]
    print(file_lst, '\n')
    for file in file_lst:
        print(file)
        with open(path + file, 'r') as fd:
            for row in fd:
                sv_lst = parsing_RANGEA(row)
                # print(sv_lst)
            print(sv_lst)
            print()