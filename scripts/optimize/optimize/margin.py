import copy
from .judge import operation_judge ,operation_judge2
from .calculator import betac, shunt_calc
from .data import Data
import numpy as np
import pandas as pd
import concurrent.futures
import matplotlib.pyplot as plt

import shutil
import os

def optimize(data : Data, directory : str):
    # 今のところは10回の回数制限とbreakで処理
    # 後々、制限を変更したい
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.mkdir(directory)

    for j in range(15):
        #　5回のばらつきシュミレーション
        copied_data = copy.deepcopy(data)

        pre_min_index = None
        for i in range(10):
            print("ばらつき"+str(j)+" : "+str(i)+"回目の最適化開始")

            if j > 0:
                scatter_apply(copied_data.vdf)

            margins = get_margins(copied_data)

            plot(margins, directory+"/"+str(j)+"-"+str(i)+".png")
            copied_data.vdf.to_csv(directory+"/"+str(j)+"-"+str(i)+"value.csv")

            min_margin = 100
            min_index = None
            for element in margins.index:
                if not copied_data.vdf.at[element,'fix']:
                    # 最小マージンの素子を探す。
                    if abs(margins.at[element,'low(%)']) < min_margin or abs(margins.at[element,'high(%)']) < min_margin:
                        min_margin = min(abs(margins.at[element,'low(%)']), abs(margins.at[element,'high(%)']))
                        min_index = element
            
            print("最小マージン : ", min_index, "  ", min_margin)

            with open(directory+"/"+str(j)+"-"+str(i)+".txt", 'w') as f:
                f.write("最小マージン : "+ str(min_index)+ "  "+ str(min_margin)+'\n') 

            # 同じものが最適化対象になってしまったら終了
            if pre_min_index == min_index:
                print("ばらつき"+str(j)+" : "+str(i)+"回目の最適化終了")
                break

            # 最小マージンが0であれば終了
            if min_margin == 0:
                print("ばらつき"+str(j)+" : "+str(i)+"回目の最適化終了")
                break

            pre_min_index = min_index

            # 最大マージンと最小マージンの中間点を次の最適化対象にする。
            copied_data.vdf.at[min_index,'main'] = ( margins.at[min_index,'low(value)'] + margins.at[min_index,'high(value)'] )/2

            print("ばらつき"+str(j)+" : "+str(i)+"回目の最適化終了")
        


    

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
        # ------

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

        if filename != None:
            fig.savefig(filename)
            plt.close(fig)

        

def __get_margin(data : Data, target_ele : str, accuracy : int = 7):
    
    copied_df : pd.DataFrame = copy.deepcopy(data.vdf)

    # デフォルト値の抽出
    default_v = copied_df.at[target_ele,'sub']
    fix_para = copied_df.at[target_ele,'fix']

    if not __filtered_simulation(data, copied_df):
        return {"index" : target_ele, "result" : (fix_para, 0, 0, 0, 0)}
    # lower    
    high_v = default_v
    low_v = 0
    target_v = (high_v + low_v)/2

    for i in range(accuracy):

        # copied_df['sub'] = copied_df['main']
        copied_df.at[target_ele,'sub'] = target_v
        if __filtered_simulation(data, copied_df):
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

        # copied_df['sub'] = copied_df['main']
        copied_df.at[target_ele,'sub'] = target_v

        if __filtered_simulation(data, copied_df):
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

    del copied_df

    return {"index" : target_ele, "result" : (fix_para, lower_margin, lower_margin_rate, upper_margin, upper_margin_rate)}

def __filtered_simulation(data : Data, df : pd.DataFrame):
    tmp_sim_data = data.sim_data
    for index in df.index:
        tmp_sim_data = tmp_sim_data.replace('#('+index+')', str(df.at[index, 'sub']))
    
    return  operation_judge2(data.time_start, data.time_stop, tmp_sim_data, data.squids, data.default_result)



def shunt_apply(vdf : pd.DataFrame):
        for index in vdf.index:
            if vdf.at[index, 'shunt'] != None:
                shunt_index = vdf.at[index, 'shunt']
                vdf.at[shunt_index, 'sub'] = shunt_calc(area=vdf.at[index, 'sub']) 

def scatter_apply(vdf : pd.DataFrame):
    for index in vdf.index:
        if vdf.at[index,'dp']:
            tmp = vdf.at[index,'sub']
            dpv = vdf.at[index,'dpv']
            vdf.at[index,'sub'] = np.random.normal(tmp,tmp*dpv/200)










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