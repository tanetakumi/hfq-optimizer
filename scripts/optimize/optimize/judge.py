from matplotlib.pyplot import legend
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
        newDataframe.plot(legend=False)
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

    resultframe.sort_values(['element', 'phase'], inplace=True)
    return resultframe


def compareDataframe(df1 : pd.DataFrame, df2 : pd.DataFrame, delay_time : float = 1.0e-10) -> bool:
    print(df1)
    print(df2)
    for index in df1.index:
        if df1.at[index, 'element'] == df2.at[index, 'element'] and df1.at[index, 'phase'] == df2.at[index, 'phase']:
            time_df1 = df1.at[index, 'time']
            time_df2 = df2.at[index, 'time']
            if time_df2 < time_df1 - delay_time or time_df1 + delay_time < time_df2:
                return False
        else:
            return False
    return True



def operation_judge(time1 : float, time2 : float, data : str, squids : list, df_result : pd.DataFrame):
    result_df = judge(time1, time2, simulation(data), squids)
    return compareDataframe(df_result, result_df)


def operation_judge2(time1 : float, time2 : float, data : str, squids : list, default_result : pd.DataFrame, delay_time : float = 5.0e-11):
    res = judge(time1, time2, simulation(data), squids)
    if default_result.drop('time', axis=1).equals(res.drop('time', axis=1)):
        for index in default_result.index:
            if default_result.at[index, 'element'] == res.at[index, 'element'] and default_result.at[index, 'phase'] == res.at[index, 'phase']:
                time_df1 = default_result.at[index, 'time']
                time_df2 = res.at[index, 'time']
                if time_df2 < time_df1 - delay_time or time_df1 + delay_time < time_df2:
                    return False
            else:
                return False
        return True    
    else:
        return False
    
