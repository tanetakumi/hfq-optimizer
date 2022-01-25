from heapq import merge

from optimize.margin_old import margin
from .judge import judge, compareDataframe
from .pyjosim import simulation
from .data import Data
from .util import vround
import pandas as pd
import concurrent.futures
import matplotlib.pyplot as plt

class Optimize:
    def __init__(self, data : Data):
        # コラムの保存、間違えて代入しないため
        self.margin_columns_list = ['low(value)', 'low(%)', 'high(value)', 'high(%)']
        # data の保存
        self.data = data

        # self.margins = pd.DataFrame()
        if data.default_result.empty:
            raise ValueError("デフォルト値でのシュミレーションがされていません。")

    def margin(self, accuracy : int = 8, thread : int = 16) -> pd.DataFrame:

        futures = []
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=thread)
        
        # tmp_dataに落とす。
        tmp_data = self.data
        margin_df = self.data.v_df

        for index_main, row_main in margin_df.iterrows():
            future = executor.submit(self.__get_margin, tmp_data, index_main, row_main, accuracy)
            futures.append(future)

        # result を受け取る dataframe
        margin_result = pd.DataFrame(columns = self.margin_columns_list)
        
        for future in concurrent.futures.as_completed(futures):
            # 結果を受け取り
            result_dic= future.result()
            # variables dataframeに追加
            margin_result.loc[result_dic["index"]] = result_dic["result"]

        # 現在のcolumns listを落として、今回の結果を入力する
        margin_df.drop(columns = self.margin_columns_list, inplace=True, errors='ignore')
        margin_df = pd.merge(margin_df, margin_result, left_index=True, right_index=True)

        # data をself.data に代入
        self.data.v_df = margin_df

        return self.data.v_df

    def plot(self, filename = None):
        
        # 全体フォントサイズ
        plt.rcParams["font.size"] = 15
        # color
        plot_color = '#01b8aa'
        # 図のサイズ
        fig, axes = plt.subplots(figsize=(10,5), facecolor="White", ncols=2, sharey=True)
        # タイトレイアウト(二つの図の隙間を埋める)
        fig.tight_layout()
        
        df = self.data.v_df.sort_index()
        index = df.index
        column0 = df['low(%)']
        column1 = df['high(%)']

        axes[0].barh(index, column0, align='center', color=plot_color)
        axes[0].set_xlim(-100, 0)
        axes[1].barh(index, column1, align='center', color=plot_color)
        axes[1].set_xlim(0, 100)
        axes[1].tick_params(axis='y', colors=plot_color)

        plt.subplots_adjust(wspace=0, top=0.85, bottom=0.1, left=0.18, right=0.95)

        if filename != None:
            fig.savefig(filename)

    def optimize(self, dirpath = None):
        
        # 今のところは10回の回数制限とbreakで処理
        # 後々、制限を変更したい
        pre_min_margin = None
        for i in range(10):
            self.margin()
            self.plot()
            min_margin = 100
            min_index = None
            for index, srs in self.data.v_df.iterrows():
                if not srs['fixed']:
                    if abs(srs['low(%)']) < min_margin or abs(srs['high(%)']) < min_margin:
                        min_margin = min(abs(srs['low(%)']), abs(srs['high(%)']))
                        min_index = index

            print("最小のマージンのindex   ",min_index)
            print(self.data.v_df)
            if pre_min_margin == min_margin:
                break
            pre_min_margin = min_margin
            
            # value 最小値にてvalue を書き換え
            self.data.v_df.at[min_index, 'value'] = vround((self.data.v_df.at[min_index, 'low(value)'] + self.data.v_df.at[min_index, 'high(value)'])/2)

        return self.data.v_df





    # concurrent.futureで回すのでselfを使わないようにしているが、これでよいのだろうか？
    def __get_margin(self, data : Data, index_main : str, row_main : pd.Series, accuracy : int):
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
def margin(data : Data, accuracy : int = 8, thread : int = 16) -> pd.DataFrame:

    # これ修正 None で帰ってきたとき empty は使えない
    if data.default_result.empty:
        print("デフォルト値でのシュミレーションがされていません。")
        return None   

    margins = pd.DataFrame(columns=['low(value)', 'low(%)', 'high(value)', 'high(%)'])

    futures = []
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=thread)

    for index_main, row_main in data.v_df.iterrows():
        future = executor.submit(get_margin, data, index_main, row_main, accuracy)
        futures.append(future)

    for future in concurrent.futures.as_completed(futures):
        result_dic= future.result()
        # variables dataframeに追加
        margins.loc[result_dic["index"]] = result_dic["result"]

    return pd.concat([data.v_df, margins], axis=1)

def get_margin(data : Data, index_main : str, row_main : pd.Series, accuracy : int):
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
    upper_margin_rate = vround((upper_margin - default_v) * 100 / default_v)

    return {"index" : index_main, "result" : (lower_margin, lower_margin_rate, upper_margin, upper_margin_rate)}



def get_margin(data : Data, index_main : str, row_main : pd.Series, accuracy : int):

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
    upper_margin_rate = vround((upper_margin - default_v) * 100 / default_v)

    return {"index" : index_main, "result" : (lower_margin, lower_margin_rate, upper_margin, upper_margin_rate)}


def margin_plot(df : pd.DataFrame, filename = None):
    df.sort_index(inplace=True)
    plt.rcParams["font.size"] = 15

    plot_color = '#01b8aa'
    index = df.index
    column0 = df['low(%)']
    column1 = df['high(%)']

    fig, axes = plt.subplots(figsize=(10,5), facecolor="White", ncols=2, sharey=True)
    fig.tight_layout()
    
    axes[0].barh(index, column0, align='center', color=plot_color)
    axes[0].set_xlim(-100, 0)
    axes[1].barh(index, column1, align='center', color=plot_color)
    axes[1].set_xlim(0, 100)
    axes[1].tick_params(axis='y', colors=plot_color)

    plt.subplots_adjust(wspace=0, top=0.85, bottom=0.1, left=0.18, right=0.95)
    # 
    if filename != None:
        fig.savefig(filename)

"""




