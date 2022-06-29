import re
import pandas as pd
from .util import stringToNum, isfloat, isint, vaild_number
from .pyjosim import simulation
from .judge3 import compare_switch_timmings, judge
from .calculator import shunt_calc, rand_norm
import numpy as np
import concurrent
import copy
import matplotlib.pyplot as plt
import os
import shutil

# ----- Matplotlib の rc 設定 ----
config = {
    "font.size":18,
    "axes.grid":True,
    "figure.figsize":[10.0, 7.0],
    "legend.fontsize": 18,
    "lines.linewidth": 3
}
plt.rcParams.update(config)


class Data:
    def __init__(self, raw_data : str, show : bool = False, plot : bool = True):
        self.vdf, self.sim_data = self.__get_variable(raw=raw_data)
        self.time_start= float(self.__get_value(raw_data, "EndTimeOfBiasRise"))
        self.time_stop = float(self.__get_value(raw_data, "StartTimeOfPulseInput"))
        self.time_delay = float(self.__get_value(raw_data, "PulseDelay"))
        self.pulse_interval = float(self.__get_value(raw_data, "PulseInterval"))
        self.squids = self.__get_judge_spuid(raw_data)
        self.default_result = self.__default_simulation(plot=plot)

        if show:
            print("--- List of variables to optimize ---")
            print(self.vdf)
            print('\n')
            print("--- Period to calculate the initial value of bias ---")
            print(self.time_start, " ~ ", self.time_stop)
            print('\n')
            print("--- SQUID used for judging the operation ---")
            print(self.squids)
            print('\n')
            print("--- Clock Pulse Interval ---")
            print(self.pulse_interval)
            print('\n')
            print("--- timming of JJ switches ---")
            for l in self.default_result:
                print(l)


    def __get_variable(self, raw : str) -> tuple:
        df = pd.DataFrame()
        
        vlist = re.findall('#.+\(.+?\)',raw)

        for raw_line in vlist:
            li = re.sub('\s','',raw_line)
            char = re.search('#.+?\(',li, flags=re.IGNORECASE).group()
            char = re.sub('#|\(','',char)
            if not df.empty and char in df.index.tolist():
                continue
            dic = {'def': None, 'main': None, 'sub': None, 'element':None,'fix': False ,'upper': None, 'lower': None ,'shunt': None,'dp': True,'dpv': None,'tmp': 0}
            
            
            m = re.search('\(.+?\)',li).group()
            m = re.sub('\(|\)','',m)
            spl = re.split(',',m)
            if len(spl)==1:
                if isfloat(spl[0]) or isint(spl[0]):
                    num = stringToNum(spl[0])
                    dic['def'] = num
                    dic['main'] = num
                    dic['sub'] = num
            for sp in spl:
                val = re.split('=',sp)
                if len(val) == 1:
                    if isfloat(val[0]) or isint(val[0]):
                        num = stringToNum(spl[0])
                        dic['def'] = num
                        dic['main'] = num
                        dic['sub'] = num
                elif len(val) == 2:
                    if re.fullmatch('v|value',val[0],flags=re.IGNORECASE):
                        num = stringToNum(val[1])
                        dic['def'] = num
                        dic['main'] = num
                        dic['sub'] = num
                    elif re.fullmatch('fix|fixed',val[0],flags=re.IGNORECASE):
                        if re.fullmatch('true',val[1],flags=re.IGNORECASE):
                            dic['fix'] = True
                    elif re.fullmatch('shunt',val[0],flags=re.IGNORECASE):
                        dic['shunt'] = val[1]
                    elif re.fullmatch('dp',val[0],flags=re.IGNORECASE):
                        if re.fullmatch('false',val[1],flags=re.IGNORECASE):
                            dic['dp'] = False
                    elif re.fullmatch('dpv',val[0],flags=re.IGNORECASE):
                        num = stringToNum(val[1])
                        dic['dpv'] = num
                    elif re.fullmatch('upper',val[0],flags=re.IGNORECASE):
                        num = stringToNum(val[1])
                        dic['upper'] = num
                    elif re.fullmatch('lower',val[0],flags=re.IGNORECASE):
                        num = stringToNum(val[1])
                        dic['lower'] = num
                    else:
                        raise ValueError("[ "+sp+" ]の記述が読み取れません。")
                else:
                    raise ValueError("[ "+sp+" ]の記述が読み取れません。")

            for line in raw.splitlines():
                if raw_line in line:
                    if re.fullmatch('R',line[0:1],flags=re.IGNORECASE):
                        dic['element'] = 'R'
                        if dic['dpv'] == None:
                            dic['dpv'] = 7
                    elif re.fullmatch('L',line[0:1],flags=re.IGNORECASE):
                        dic['element'] = 'L'
                        if dic['dpv'] == None:
                            dic['dpv'] = 7
                    elif re.fullmatch('C',line[0:1],flags=re.IGNORECASE):
                        dic['element'] = 'C'
                        if dic['dpv'] == None:
                            dic['dpv'] = 7
                    elif re.fullmatch('V',line[0:1],flags=re.IGNORECASE):
                        dic['element'] = 'V'
                        if dic['dpv'] == None:
                            dic['dpv'] = 7
                    elif re.fullmatch('B',line[0:1],flags=re.IGNORECASE):
                        dic['element'] = 'B'
                        if dic['dpv'] == None:
                            dic['dpv'] = 7
                    else:
                        dic['element'] = None
                        if dic['dpv'] == None:
                            dic['dpv'] = 7
                    break
            
            dic_df = pd.DataFrame.from_dict({ char : dic }, orient = "index")
            df = pd.concat([df, dic_df])

        raw = re.sub('\*+\s*optimize[\s\S]+$','', raw)

        for v in re.findall('#.+\(.+?\)',raw):
            ch = re.search('#.+?\(',v).group()
            ch = re.sub('#|\(','',ch)
            ch = "#("+ch+")"
            raw = raw.replace(v, ch)
            
        return df , raw




    def __get_value(self, raw, key) -> str:
        m_object = re.search(key+'=[\d\.\+e-]+', raw, flags=re.IGNORECASE)
        if m_object:
            return re.split('=', m_object.group())[1]
        else:
            raise ValueError("[ "+key+" ]の値が読み取れません。")

    def __get_judge_spuid(self, raw : str) -> list:
        squids = []
        tmp = []
        for line in raw.splitlines():
            p_obj = re.search('\.print\s+phase.+',line, flags=re.IGNORECASE)
            v_obj = re.search('\.print\s+devv.+',line, flags=re.IGNORECASE)
            # 連続であることから　m_obj = None　になるまで　tmp に追加する。
            if p_obj:
                data_sub = re.sub('\s|\.print|phase','',p_obj.group(), flags=re.IGNORECASE)
                tmp.append('P('+data_sub.upper()+')')
            else:
                if len(tmp)>0:
                    squids.append(tmp)
                    tmp = []
            # 電圧の時
            if v_obj:
                data_sub = re.sub('\s|\.print|devv','',v_obj.group(), flags=re.IGNORECASE)
                squids.append(['V('+data_sub.upper()+')'])
            
        return squids


    def __default_simulation(self,  plot = True) -> pd.DataFrame:
        df = self.data_simulation(self.vdf['def'])
        if plot: 
            # print("default 値でのシュミレーション結果")
            df.plot(legend=False)
            plt.xlabel("Time(s)", size=18)# x軸指定
        return judge(self.time_start, self.time_stop, self.pulse_interval, df, self.squids, plot)


    def data_simulation(self, parameter : pd.Series) -> pd.DataFrame:
        copied_sim_data = self.sim_data
        for index in parameter.index:
            copied_sim_data = copied_sim_data.replace('#('+index+')', str(parameter[index]))

        df = simulation(copied_sim_data)
        return df


    def __operation_judge(self, parameter : pd.Series):
        res = judge(self.time_start, self.time_stop, self.pulse_interval, self.data_simulation(parameter), self.squids)
        return compare_switch_timmings(res, self.default_result,self.time_delay)


    def get_margins(self, plot : bool = False, accuracy : int = 8, thread : int = 8) -> pd.DataFrame:
        margin_columns_list = ['low(value)', 'low(%)', 'high(value)', 'high(%)']

        futures = []
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=thread)
        for index in self.vdf.index:
            future = executor.submit(self.__get_margin, self.vdf['sub'], index, accuracy)
            futures.append(future)

        # result を受け取る dataframe
        margin_result = pd.DataFrame(columns = margin_columns_list)
        
        for future in concurrent.futures.as_completed(futures):
            # 結果を受け取り
            result_dic= future.result()
            # variables dataframeに追加
            margin_result.loc[result_dic["index"]] = result_dic["result"]

        if plot:
            self.__plot(margin_result)

        return margin_result


    def __get_margin(self, srs : pd.Series, target_ele : str, accuracy : int = 7):

        # deepcopy　をする
        parameter : pd.Series = copy.deepcopy(srs)

        # デフォルト値の抽出
        default_v = parameter[target_ele]

        # 0%の値は動くか確認
        if not self.__operation_judge(parameter):
            return {"index" : target_ele, "result" : (0, 0, 0, 0)}

        # lower ----------------- 
        high_v = default_v
        low_v = 0
        target_v = (high_v + low_v)/2

        for i in range(accuracy):
            parameter[target_ele] = target_v
            if self.__operation_judge(parameter):
                high_v = target_v
                target_v = (high_v + low_v)/2
            else:
                low_v = target_v
                target_v = (high_v + low_v)/2

        lower_margin = high_v
        lower_margin_rate = (lower_margin - default_v) * 100 / default_v
        # -----------------

        # upper -----------------
        high_v = 0
        low_v = default_v
        target_v = default_v * 2

        for i in range(accuracy):

            parameter[target_ele] = target_v
            if self.__operation_judge(parameter):
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
        # -----------------

        # deepcopy　したものを削除
        del parameter

        return {"index" : target_ele, "result" : (lower_margin, lower_margin_rate, upper_margin, upper_margin_rate)}


    
    def optimize(self, directory : str, l1c=10, l2c=40):

        # ------------------------------ #
        # 変数
        #
        #
        # ------------------------------ #
        diff_margin_parcentage = 0.2
        loop1_count = l1c
        loop2_count = l2c



        # directory の処理
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.mkdir(directory)

        
        first_min_margin = 0 # loop 1 のマージン

        
        for k in range(loop1_count):

            # -------- loop 1 --------

            second_min_margin = 0     # loop 2 のマージン
            margins_for_plot = None   # 保存するためのマージン保管場所
            main_parameter = None     # 最適解のパラメータ

            
            for j in range(loop2_count):

                # -------- loop 2 --------

                self.vdf['sub'] = self.vdf['main'] 
                self.shunt_apply()
                # 最初の一回はそのままのマージンを計算
                if j > 0:
                    self.scatter_apply()
                
                pre_min_index = None    # ひとつ前の最小マージンを取るindex
                for i in range(10):
                    print(str(k)+":"+str(j)+":"+str(i)+"の最適化")
                    # マージンの計算
                    margins = self.get_margins()

                    min_margin = 100
                    
                    min_index = None
                    for element in margins.index:
                        if not self.vdf.at[element,'fix']:
                            # 最小マージンの素子を探す。
                            if abs(margins.at[element,'low(%)']) < min_margin or abs(margins.at[element,'high(%)']) < min_margin:
                                min_margin = vaild_number(min(abs(margins.at[element,'low(%)']), abs(margins.at[element,'high(%)'])), 4)
                                min_index = element
                    
                    if 'BIAS' in margins.index:
                        bias_margin =  vaild_number(min(abs(margins.at['BIAS','low(%)']), abs(margins.at['BIAS','high(%)'])), 4)
                        print("バイアスマージン : ",bias_margin)

                    print("最小マージン : ", min_index, "  ", min_margin)

                    #　logへのマージンの書き込み
                    with open(directory+"/log.txt", 'a') as f:
                        f.write(str(k)+":"+str(j)+":"+str(i)+"の最小マージン : "+ str(min_index)+ "  "+ str(min_margin)+'\n') 

                    
                    if min_margin > second_min_margin:
                        print("最適値の更新"+str(k)+":"+str(j)+":"+str(i)+"の最適化  ", min_margin, "%")
                        margins_for_plot = margins
                        second_min_margin = min_margin
                        main_parameter = copy.copy(self.vdf['sub'])

                    else:
                        if min_margin + diff_margin_parcentage > second_min_margin:
                            self.vdf['sub'].to_csv(directory+"/"+str(k)+"-"+str(j)+"-"+str(i)+"-sub.csv")

    
                    # -------------------------- #
                    # ループ2 終了条件
                    # 1. 最小マージンが0
                    # 2. 同じものが最適化対象になる
                    # -------------------------- #                  
                    if min_margin == 0:     # 最小マージンが0
                        break

                    if pre_min_index == min_index:      # 同じものが最適化対象
                        break
                    pre_min_index = min_index



                    # 最大マージンと最小マージンの中間点を次の最適化対象にする。最小値最大値を考慮
                    shifted_value = ( margins.at[min_index,'low(value)'] + margins.at[min_index,'high(value)'] )/2
                    lower_limit = self.vdf.at[min_index,'lower']
                    upper_limit = self.vdf.at[min_index,'upper']

                    if lower_limit != None and shifted_value < lower_limit:
                        self.vdf.at[min_index,'sub'] = lower_limit
                    elif upper_limit != None and shifted_value < upper_limit:
                        self.vdf.at[min_index,'sub'] = upper_limit
                    else:
                        self.vdf.at[min_index,'sub'] = shifted_value

                # -------- loop 2 end --------


            # -------------------------- #
            # ループ1 終了条件
            # 1. 最小マージンが改善されない
            # -------------------------- #
            if second_min_margin > first_min_margin:
                print("--- "+str(k)+":x:x"+"の最適化  ", second_min_margin, "% ---")
                first_min_margin = second_min_margin
                self.vdf['main'] = main_parameter
                

                # 保存する
                print("保存")
                self.__plot(margins_for_plot, directory+"/"+str(k)+"-x.png")
                main_parameter.to_csv(directory+"/"+str(k)+"-main.csv")
                with open(directory+"/"+str(k)+"-netlist.txt","w") as f:
                    copied_sim_data = self.sim_data
                    for index in main_parameter.index:
                        copied_sim_data = copied_sim_data.replace('#('+index+')', '#'+index+'('+ str(vaild_number(main_parameter[index],3))+')')
                    f.write(copied_sim_data)

            else:
                print("最適化終了")
                break


    def shunt_apply(self):
        for index in self.vdf.index:
            if self.vdf.at[index, 'shunt'] != None:
                shunt_index = self.vdf.at[index, 'shunt']
                self.vdf.at[shunt_index, 'sub'] = shunt_calc(area=self.vdf.at[index, 'sub']) 


    def scatter_apply(self):
        for index in self.vdf.index:
            if self.vdf.at[index,'dp']:
                tmp = self.vdf.at[index,'sub']
                dpv = self.vdf.at[index,'dpv']
                up = self.vdf.at[index,'upper']
                lo = self.vdf.at[index,'lower']
                self.vdf.at[index,'sub'] = rand_norm(tmp, tmp*dpv/200, up, lo)


    def __plot(self, margins : pd.DataFrame, filename = None):
        # バーのcolor
        plot_color = '#01b8aa'

        df = margins.sort_index()
        index = df.index
        column0 = df['low(%)']
        column1 = df['high(%)']

        # --- biasのカラーを変更したリスト ---
        index_color = []
        for i in index:
            if re.search('bias|Vb',i,flags=re.IGNORECASE):
                index_color.append('red')
            else:
                index_color.append(plot_color)
        # ------

        # 図のサイズ　sharey:グラフの軸の共有(y軸)
        fig, axes = plt.subplots(figsize=(10, len(index)/2.5), ncols=2, sharey=True)
        plt.subplots_adjust(wspace=0)
        plt.suptitle('Margins')
        axes[0].set_ylabel("Elements", fontsize=20)
        axes[1].set_xlabel("%", fontsize=20)

        # 分割した 0 グラフ
        axes[0].barh(index, column0, align='center', color=index_color)
        axes[0].set_xlim(-100, 0)
        axes[0].grid(axis='y')


        # 分割した 1 グラフ
        axes[1].barh(index, column1, align='center', color=index_color)
        axes[1].set_xlim(0, 100)
        axes[1].tick_params(axis='y', colors=plot_color)  # 1 グラフのメモリ軸の色をプロットの色と合わせて見れなくする
        axes[1].grid(axis='y')


        if filename != None:
            fig.savefig(filename)
            plt.close(fig)