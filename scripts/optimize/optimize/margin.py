import copy
from .judge import operation_judge
from .calculator import betac
from .data import Data
import numpy as np
import pandas as pd
import concurrent.futures
import matplotlib.pyplot as plt

def optimize(data : Data, directory : str):
    # 今のところは10回の回数制限とbreakで処理
    # 後々、制限を変更したい
    pre_min_index = None
    for i in range(10):
        print(str(i)+"回目の最適化開始")
        print(data.vdf)
        margins = get_margins(data)
        # print(margins)
        plot(margins, directory+"/"+str(i)+".png")
        min_margin = 100
        min_index = None
        for element in margins.index:
            if not data.vdf.at[element,'fix']:
                if abs(margins.at[element,'low(%)']) < min_margin or abs(margins.at[element,'high(%)']) < min_margin:
                    min_margin = min(abs(margins.at[element,'low(%)']), abs(margins.at[element,'high(%)']))
                    min_index = element
        
        print("最小マージン : ", min_index, "  ", min_margin)
        
        if pre_min_index == min_index:
            break
        pre_min_index = min_index

        data.vdf.at[min_index,'main'] = ( margins.at[min_index,'low(value)'] + margins.at[min_index,'high(value)'] )/2
        print(str(i)+"回目の最適化終了")

def get_margins(data : Data, accuracy : int = 8, thread : int = 8) -> pd.DataFrame:
    margin_columns_list = ['fix','low(value)', 'low(%)', 'high(value)', 'high(%)']

    futures = []
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=thread)

    for index in data.vdf.index:
        future = executor.submit(__get_margin, data, index, accuracy)
        futures.append(future)

    # result を受け取る dataframe
    margin_result = pd.DataFrame(columns = margin_columns_list)
    
    for future in concurrent.futures.as_completed(futures):
        # 結果を受け取り
        result_dic= future.result()
        # variables dataframeに追加
        margin_result.loc[result_dic["index"]] = result_dic["result"]

    # 現在のcolumns listを落として、今回の結果を入力する
    # tmp_sim_data.v_df.drop(columns = margin_columns_list, inplace=True, errors='ignore')
    # margin_df = pd.merge(margin_df, margin_result, left_index=True, right_index=True)
    
    return margin_result


def plot(vdf, filename = None):
        # バーのcolor
        plot_color = '#01b8aa'

        df = vdf.sort_index()
        index = df.index
        column0 = df['low(%)']
        column1 = df['high(%)'] 
        # --- biasのカラーを変更したリスト ---
        index_color = []
        import re
        for i in index:
            if re.search('bias|Vb',i,flags=re.IGNORECASE):
                index_color.append('red')
            else:
                index_color.append(plot_color)
        # --- ---


        # 図のサイズ　sharey:グラフの軸の共有(y軸)
        fig, axes = plt.subplots(figsize=(10,len(index)/3),ncols=2, sharey=True)
        plt.subplots_adjust(wspace=0)
        fig.suptitle("Operation Margin", fontsize=15)

        # 分割した 0 グラフ
        axes[0].barh(index, column0, align='center', color=index_color)
        axes[0].set_xlim(-100, 0)
        axes[0].tick_params(labelsize=15)
        # 分割した 1 グラフ
        axes[1].barh(index, column1, align='center', color=index_color)
        axes[1].set_xlim(0, 100)
        axes[1].tick_params(labelsize=15)
        axes[1].tick_params(axis='y', colors=plot_color)  # 1 グラフのメモリ軸の色をプロットの色と合わせて見れなくする

        # plt.subplots_adjust(wspace=0, top=0.85, bottom=0.1, left=0.18, right=0.95)
        

        if filename != None:
            fig.savefig(filename)

def __get_margin(data : Data, target_ele : str, accuracy : int = 7):

    vdf : pd.DataFrame = copy.copy(data.vdf)

    # デフォルト値の抽出
    default_v = vdf.at[target_ele,'main']
    fix_para = vdf.at[target_ele,'fix']

    # lower    
    high_v = default_v
    low_v = 0
    target_v = (high_v + low_v)/2

    for i in range(accuracy):

        vdf['sub'] = vdf['main']
        vdf['tmp'] = 0
        vdf.at[target_ele,'tmp'] = 1
        vdf.at[target_ele,'sub'] = target_v
        
        if __filtered_simulation(data, vdf):
            high_v = target_v
            target_v = (high_v + low_v)/2
        else:
            low_v = target_v
            target_v = (high_v + low_v)/2

    lower_margin = high_v
    lower_margin_rate = (lower_margin - default_v) * 100 / default_v

    # upper
    high_v = 0
    low_v = default_v
    target_v = default_v * 2

    for i in range(accuracy):

        vdf['sub'] = vdf['main']
        vdf['tmp'] = 0
        vdf.at[target_ele,'tmp'] = 1
        vdf.at[target_ele,'sub'] = target_v

        if __filtered_simulation(data, vdf):
            if high_v == 0:
                low_v = target_v
                break
            low_v = target_v
            target_v = (high_v + low_v)/2
        else:
            high_v = target_v
            target_v = (high_v + low_v)/2

    upper_margin = low_v
    upper_margin_rate = (upper_margin - default_v) * 100 / default_v

    del vdf
    

    return {"index" : target_ele, "result" : (fix_para, lower_margin, lower_margin_rate, upper_margin, upper_margin_rate)}

def __filtered_simulation(data : Data, df : pd.DataFrame):
    tmp_sim_data = data.sim_data
    # __betac_filter(df)
    # __lic_filter(df)
    # __scatter_filter(df)
    for index in df.index:
        tmp_sim_data = tmp_sim_data.replace('#('+index+')', str(df.at[index, 'sub']))
    return  operation_judge(data.time_start, data.time_stop, tmp_sim_data, data.squids, data.default_result)


def __betac_filter(df : pd.DataFrame):
    for index in df.index:
        if df.at[index,'tmp'] > 0 and df.at[index,'tmp'] != 2 and df.at[index,'bc'] != None:
            for tmp_index in df.index:
                # 自身と同じインデックスはスキップ
                if tmp_index == index:
                    continue
                # tag　が一致したとき
                if df.at[tmp_index,'bc'] == df.at[index,'bc']:
                    # R と B の関係であるか確認
                    if df.at[index,'element'] == 'R' and df.at[tmp_index,'element'] == 'B':
                        df.at[tmp_index,'sub'] = betac('area',Rshunt=df.at[index,'sub'])
                        df.at[tmp_index,'tmp'] = 2
                    elif df.at[index,'element'] == 'B' and df.at[tmp_index,'element'] == 'R':
                        df.at[tmp_index,'sub'] = betac('shunt',area=df.at[index,'sub'])
                        df.at[tmp_index,'tmp'] = 2
                    else:
                        raise ValueError("element1 ",df.at[index,'element'],"  element2 ",df.at[tmp_index,'element'])
                    break
            break

def __lic_filter(df : pd.DataFrame):
    for index in df.index:
        if df.at[index,'tmp'] > 0 and df.at[index,'tmp'] != 3 and df.at[index,'lic'] != None:
            for tmp_index in df.index:
                # 自身と同じインデックスはスキップ
                if tmp_index == index:
                    continue
                # tag　が一致したとき
                if df.at[tmp_index,'lic'] == df.at[index,'lic']:
                    # R と B の関係であるか確認
                    if df.at[index,'element'] == 'L' and df.at[tmp_index,'element'] == 'B':
                        df.at[tmp_index,'sub'] = df.at[index,'main'] * df.at[tmp_index,'main'] / df.at[index,'sub']
                        df.at[tmp_index,'tmp'] = 3
                    elif df.at[index,'element'] == 'B' and df.at[tmp_index,'element'] == 'L':
                        df.at[tmp_index,'sub'] = df.at[index,'main'] * df.at[tmp_index,'main'] / df.at[index,'sub']
                        df.at[tmp_index,'tmp'] = 3
                    else:
                        raise ValueError("(element1,index1)",df.at[index,'element'],index,"  element2 ",df.at[tmp_index,'element'])
                    break

def __scatter_filter(df : pd.DataFrame):
    for index in df.index:
        if df.at[index,'dp']:
            tmp = df.at[index,'sub']
            dpv = df.at[index,'dpv']
            df.at[index,'sub'] = np.random.normal(tmp,tmp*dpv/200)


























"""



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

    """