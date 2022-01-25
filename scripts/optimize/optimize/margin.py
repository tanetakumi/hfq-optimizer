from heapq import merge

from optimize.margin_old import margin
from .judge import judge, compareDataframe
from .pyjosim import simulation
from .util import vround
from .data import Data
import pandas as pd
import concurrent.futures
import matplotlib.pyplot as plt

def margin(data : Data, accuracy : int = 8, thread : int = 16) -> pd.DataFrame:
    margin_columns_list = ['low(value)', 'low(%)', 'high(value)', 'high(%)']


    futures = []
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=thread)
    
    # tmp_dataに落とす。
    tmp_data = data
    tmp_data.v_df
    # margin_df : pd.DataFrame = data.v_df

    for index_main, row_main in tmp_data.v_df.iterrows():
        future = executor.submit(__get_margin, tmp_data, index_main, row_main, accuracy)
        futures.append(future)

    # result を受け取る dataframe
    margin_result = pd.DataFrame(columns = margin_columns_list)
    
    for future in concurrent.futures.as_completed(futures):
        # 結果を受け取り
        result_dic= future.result()
        # variables dataframeに追加
        margin_result.loc[result_dic["index"]] = result_dic["result"]

    # 現在のcolumns listを落として、今回の結果を入力する
    tmp_data.v_df.drop(columns = margin_columns_list, inplace=True, errors='ignore')
    # margin_df = pd.merge(margin_df, margin_result, left_index=True, right_index=True)

    return tmp_data

def get_operation(data : Data):
    result_df = judge(data.time_start, data.time_stop, simulation(data.sim_data), data.squids)
    return compareDataframe(result_df, data.default_result)
    
# concurrent.futureで回すのでselfを使わないようにしているが、これでよいのだろうか？
def __get_margin(data : Data, index_main : str, row_main : pd.Series, accuracy : int):
    variables : pd.DataFrame = data.v_df
    sim_data : str = data.sim_data


    # シュミレーションデータの作成
    for index_tmp, row_tmp in variables.iterrows():
        if index_main != index_tmp:
            sim_data = sim_data.replace(row_tmp['text'], str(row_tmp['value']))

    # lower
    default_v = row_main['value']
    high_v = default_v
    low_v = 0
    target_v = vround((high_v + low_v)/2) 

    for i in range(accuracy):
        tmp_sim_data = sim_data.replace(row_main['text'], str(target_v))
        tmp_df = judge(data.time_start, data.time_stop, simulation(tmp_sim_data), data.squids)
        if compareDataframe(tmp_df, data.default_result):
            high_v = target_v
            target_v = vround((high_v + low_v)/2) 
        else:
            low_v = target_v
            target_v = vround((high_v + low_v)/2)

    lower_margin = vround(high_v)
    lower_margin_rate = vround((lower_margin - default_v) * 100 / default_v)

    # upper
    high_v = 0
    low_v = default_v
    target_v = vround(default_v * 2)

    for i in range(accuracy):
        tmp_sim_data = sim_data.replace(row_main['text'], str(target_v))
        tmp_df = judge(data.time_start, data.time_stop, simulation(tmp_sim_data), data.squids)
        if compareDataframe(tmp_df, data.default_result):
            if high_v == 0:
                low_v = target_v
                break
            low_v = target_v
            target_v = vround((high_v + low_v)/2)
        else:
            high_v = target_v
            target_v = vround((high_v + low_v)/2)

    upper_margin = vround(low_v)
    upper_margin_rate = vround((upper_margin - default_v) * 100 / default_v, 4)

    return {"index" : index_main, "result" : (lower_margin, lower_margin_rate, upper_margin, upper_margin_rate)}