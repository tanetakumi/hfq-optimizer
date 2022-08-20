import pandas as pd
import math
import re
from .config import Config
import matplotlib.pyplot as plt
from .graph import phase_sim_plot

def get_switching_timing(config : Config, data : pd.DataFrame, plot = False) -> pd.DataFrame:

    p = math.pi
    p2 = math.pi * 2

    newDataframe = pd.DataFrame()
    if not config.phase_ele == []:
        for squid in config.phase_ele:
            if len(squid) == 1:
                newDataframe['P('+'+'.join(squid)+')'] = data['P('+squid[0]+')']
            elif len(squid) == 2:
                newDataframe['P('+'+'.join(squid)+')'] = data['P('+squid[0]+')'] + data['P('+squid[1]+')']
            elif len(squid) == 3:
                newDataframe['P('+'+'.join(squid)+')'] = data['P('+squid[0]+')'] + data['P('+squid[1]+')'] + data['P('+squid[2]+')']
        
        phase_sim_plot(newDataframe)

        resultframe = []
        for column_name, srs in newDataframe.iteritems():
            # バイアスをかけた時の状態の位相(初期位相)
            init_phase = srs[( srs.index > config.start_time ) & ( srs.index < config.end_time )].mean()
            
            judge_phase = init_phase + p
            
            # クロックが入ってからのものを抽出
            srs = srs[srs.index > config.end_time]

            # 位相変数
            flag = 0
            for i in range(len(srs)-1):
                if (srs.iat[i] - (flag*p2 + judge_phase)) * (srs.iat[i+1] - (flag*p2 + judge_phase)) < 0:
                    flag = flag + 1
                    resultframe.append({'time':srs.index[i], 'phase':flag, 'element':column_name})
                elif (srs.iat[i] - ((flag-1)*p2 + judge_phase)) * (srs.iat[i+1] - ((flag-1)*p2 + judge_phase)) < 0:
                    flag = flag - 1
                    resultframe.append({'time':srs.index[i], 'phase':flag, 'element':column_name})

    if not config.voltage_ele == []:
        for vol in config.voltage_ele:
            srs_std = data["V("+vol+")"].rolling(window=10).std()
            srs_std_max = srs_std.rolling(window=10).max()
            basis = srs_std_max.mean()/2
            reap = False
            tmp = 0
            flag = 1
            for i in range(len(srs_std_max)-1):
                if not reap:
                    if srs_std_max.iat[i] < basis and basis < srs_std_max.iat[i+1]:
                        srs_std_max.iat[i] = basis *2
                        tmp = srs_std_max.index[i]
                        reap = True
                else:
                    if srs_std_max.iat[i] > basis and basis > srs_std_max.iat[i+1]:
                        srs_std_max.iat[i] = - basis * 2
                        if srs_std_max.index[i] - tmp > config.pulse_interval/2:
                            resultframe.append({'time':tmp, 'phase':flag, 'element':column_name})
                            resultframe.append({'time':srs_std_max.index[i], 'phase':-flag, 'element':column_name})
                            flag = flag + 1
                        reap = False

    return resultframe


def compare_switch_timmings(dl1 : list, dl2 : list, delay_time : float = 1.0e-10) -> bool:

    def get_dict(dict_list : list, phase : int, element : str) -> float:
        for l in dict_list:
            if l['phase'] == phase and l['element'] == element:
                return l['time']
        return 0

    # Number of switches is different
    if len(dl1) == len(dl2):
        for l1 in dl1:
            l2_time = get_dict(dl2, l1['phase'], l1['element'])
            l1_time = l1['time']
            if l2_time < l1_time - delay_time or l1_time + delay_time < l2_time:
                return False
        return True
    else:
        return False
    
 