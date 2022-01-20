from .judge import judge, compareDataframe
from .pyjosim import simulation
from .data2 import Data
import pandas as pd
import concurrent.futures

def margin(data : Data, accuracy : int = 8):
    if data.default_result == None:
        print("デフォルト値でのシュミレーションがされていません。")
    
    
    variables : pd.DataFrame = data.v_df
    
    for index_main, row_main in variables.iterrows():
        sim_data : str = data.sim_data

        # シュミレーションデータの作成
        for index_tmp, row_tmp in variables.iterrows():
            if index_main != index_tmp:
                sim_data = sim_data.replace(row_tmp['text'], str(row_tmp['value']))

        # lower
        high_v = row_main['value']
        low_v = 0
        target_v = (high_v + low_v)/2   
        # 桁数の制限が欲しい ------------------
        # target_v
        # -----------------------------------

        for i in range(accuracy):
            tmp_sim_data = sim_data.replace(row_main['text'], str(target_v))
            tmp_df = judge(data.time_start, data.time_stop, simulation(tmp_sim_data), data.squids)
            if compareDataframe(tmp_df, data.default_result):
                high_v = target_v
                target_v = (high_v + low_v)/2
            else:
                low_v = target_v
                target_v = (high_v + low_v)/2

        lower_margin = high_v

        # upper
        high_v = 0
        low_v = row_main['value']
        target_v = row_main['value'] * 2

        for i in range(accuracy):
            tmp_sim_data = sim_data.replace(row_main['text'], str(target_v))
            tmp_df = judge(data.time_start, data.time_stop, simulation(tmp_sim_data), data.squids)
            if compareDataframe(tmp_df, data.default_resultdef_df):
                
                low_v = target_v
                if high_v == 0:
                    break
                target_v = (high_v + low_v)/2
            else:
                high_v = target_v
                target_v = (high_v + low_v)/2

        upper_margin = low_v
    
    
    return {'char' : target['char'], 'def': target['def'], 
            'lower': round((lower_margin-target['def'])/target['def']*100,2), 'lower_value': lower_margin,
            'upper' : round((upper_margin-target['def'])/target['def']*100,2), 'upper_value' : upper_margin}   