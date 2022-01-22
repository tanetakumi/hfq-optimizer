from .judge import judge, compareDataframe
from .pyjosim import simulation
from .data2 import Data
from .util import vround
import pandas as pd
import concurrent.futures
import matplotlib.pyplot as plt

class Optimize:
    def __init__(self, data : Data):
        self.data = data
        self.margins = pd.DataFrame()
        if data.default_result.empty:
            raise ValueError("デフォルト値でのシュミレーションがされていません。")

    def margin(self, accuracy : int = 8, thread : int = 16) -> pd.DataFrame:

        self.margins = pd.DataFrame(columns=['low(value)', 'low(%)', 'high(value)', 'high(%)'])

        futures = []
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=thread)

        for index_main, row_main in self.data.v_df.iterrows():
            future = executor.submit(self.__get_margin, self.data, index_main, row_main, accuracy)
            futures.append(future)

        for future in concurrent.futures.as_completed(futures):
            result_dic= future.result()
            # variables dataframeに追加
            self.margins.loc[result_dic["index"]] = result_dic["result"]

        return pd.concat([self.data.v_df, self.margins], axis=1)

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
        upper_margin_rate = vround((upper_margin - default_v) * 100 / default_v)

        return {"index" : index_main, "result" : (lower_margin, lower_margin_rate, upper_margin, upper_margin_rate)}
    
    def plot(self, filename = None):
        
        # 全体フォントサイズ
        plt.rcParams["font.size"] = 15
        # color
        plot_color = '#01b8aa'
        # 図のサイズ
        fig, axes = plt.subplots(figsize=(10,5), facecolor="White", ncols=2, sharey=True)
        # タイトレイアウト(二つの図の隙間を埋める)
        fig.tight_layout()
        
        df = self.margins.sort_index()
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

    def optimize(self):
        min_margin = 100
        min_index = None
        for index, srs in self.margins.iterrows():
            if not srs['fixed']:
                if abs(srs['low(%)']) < min_margin or abs(srs['high(%)']) < min_margin:
                    min_margin = min(abs(srs['low(%)']), abs(srs['high(%)']))
                    min_index = index



"""
def margin(data : Data, accuracy : int = 8, thread : int = 16) -> pd.DataFrame:

    # これ修正　None で帰ってきたとき　empty　は使えない
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




