import pandas as pd
import math
from .pyjosim import simulation


def judge(time1 : float, time2 : float, data : pd.DataFrame, judge_squids : list, plot = False) -> pd.DataFrame:

    p = math.pi
    p2 = math.pi * 2

    newDataframe = pd.DataFrame()
    for squid in judge_squids:
        if len(squid) == 1:
            newDataframe[''.join(squid)] = data[squid[0]]
        elif len(squid) == 2:
            newDataframe[''.join(squid)] = data[squid[0]] + data[squid[1]]
        elif len(squid) == 3:
            newDataframe[''.join(squid)] = data[squid[0]] + data[squid[1]] + data[squid[2]]
    if plot:
        newDataframe.plot()
    resultframe = pd.DataFrame(columns=['time', 'element', 'phase'])
    for column_name, srs in newDataframe.iteritems():

        # バイアスをかけた時の状態の位相(初期位相)
        init_phase = srs[( srs.index > time1 ) & ( srs.index < time2 )].mean()
        
        judge_phase = init_phase + p
        
        # クロックが入ってからのものを抽出
        srs = srs[srs.index > time2]

        # 位相変数
        flag = 0
        for i in range(len(srs)-1):
            if (srs.iat[i] - (flag*p2 + judge_phase)) * (srs.iat[i+1] - (flag*p2 + judge_phase)) < 0:
                flag = flag + 1
                resultframe = resultframe.append({'time':srs.index[i], 'element':column_name, 'phase':flag},ignore_index=True)
            elif (srs.iat[i] - ((flag-1)*p2 + judge_phase)) * (srs.iat[i+1] - ((flag-1)*p2 + judge_phase)) < 0:
                flag = flag - 1
                resultframe = resultframe.append({'time':srs.index[i], 'element':column_name, 'phase':flag},ignore_index=True)

    return resultframe


def compareDataframe(df1 : pd.DataFrame, df2 : pd.DataFrame) -> bool:
    return df1.sort_values(['phase', 'time']).drop('time', axis=1).reset_index(drop=True)\
        .equals(df2.sort_values(['phase', 'time']).drop('time', axis=1).reset_index(drop=True))



def operation_judge(time1 : float, time2 : float, data : str, squids : list, df_result : pd.DataFrame):
    result_df = judge(time1, time2, simulation(data), squids)
    return compareDataframe(result_df, df_result) 

