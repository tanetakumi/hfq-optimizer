from locale import D_FMT
import re
import math
import pandas as pd
import numpy as np
import concurrent
import copy
import matplotlib.pyplot as plt
import os
import shutil


from .util import stringToNum, isfloat, isint, vaild_number
from .pyjosim import simulation
from .calculator import shunt_calc, rand_norm
from .config import check_config

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
    def __init__(self, raw_data : str, config : dict, show : bool = True, plot : bool = True):
        # get variable
        self.vdf, self.sim_data = self.__get_variable(raw=raw_data)

        # check config file
        if check_config(config):
            self.config = config
            
        # print(self.sim_data)
        self.sim_data = self.__create_netlist(self.sim_data,self.config)
        # print(self.sim_data)

        # 変数が存在するかしないか
        if self.vdf.empty:
            self.default_result = self.__switch_timmings(self.sim_data,plot=plot)
        else:
            self.default_result = self.__switch_timmings(self.__input_parameter(self.vdf["def"]),plot=plot)

        
        if show:
            print("--- config ---")
            for c in config:
                print(c)
            print('\n')                
            print("--- List of variables to optimize ---")
            print(self.vdf)
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
            dic = {'def': None, 'main': None, 'sub': None, 'element':None,'fix': False ,'upper': None, 'lower': None ,'shunt': None,'dp': True,'dpv': None}
            
            
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

        for v in re.findall('#.+\(.+?\)',raw):
            ch = re.search('#.+?\(',v).group()
            ch = re.sub('#|\(','',ch)
            ch = "#("+ch+")"
            raw = raw.replace(v, ch)
            
        return df , raw

    def def_sim(self, plot : bool = False):
        df = simulation(self.__input_parameter(self.vdf['def']))
        
        if plot:
            self.__plot(df)
    
    def __input_parameter(self, parameter : pd.Series) -> str:
        copied_sim_data = self.sim_data
        for index in parameter.index:
            copied_sim_data = copied_sim_data.replace('#('+index+')', str(parameter[index]))
        return copied_sim_data
    
    def get_switch_timmings(self):
        return self.default_result
    
    def __switch_timmings(self, data : str, plot = False) -> pd.DataFrame:
        df = simulation(data)

        time1 = self.config["avgcalc.start.time"]
        time2 = self.config["avgcalc.end.time"]
        pulse_interval = self.config["pulse.interval"]
        phase_ele = self.config["phase.ele"]
        voltage_ele = self.config["voltage.ele"]

        p = math.pi
        p2 = math.pi * 2

        newDataframe = pd.DataFrame()
        if not phase_ele == []:
            for elements in phase_ele:
                name = "P("+'+'.join(elements)+")"
                if len(elements) ==1:
                    newDataframe[name] = df["P("+elements[0]+")"]
                elif len(elements) ==2:
                    newDataframe[name] = df["P("+elements[0]+")"] + df["P("+elements[1]+")"]
                    

        if not voltage_ele == []:
            for ele in voltage_ele:
                newDataframe["V("+ele+")"] = df["V("+ele+")"]

        if plot:
            self.__plot(df)
            self.__plot(newDataframe)


        resultframe = []
        for column_name, srs in newDataframe.iteritems():
            if re.search('P\(.+\)',column_name, flags=re.IGNORECASE):

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
                        resultframe.append({'time':srs.index[i], 'phase':flag, 'element':column_name})
                    elif (srs.iat[i] - ((flag-1)*p2 + judge_phase)) * (srs.iat[i+1] - ((flag-1)*p2 + judge_phase)) < 0:
                        flag = flag - 1
                        resultframe.append({'time':srs.index[i], 'phase':flag, 'element':column_name})

            elif re.search('V\(.+\)',column_name, flags=re.IGNORECASE):
                srs_std = srs.rolling(window=10).std()
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
                            if srs_std_max.index[i] - tmp > pulse_interval/2:
                                resultframe.append({'time':tmp, 'phase':flag, 'element':column_name})
                                resultframe.append({'time':srs_std_max.index[i], 'phase':-flag, 'element':column_name})
                                flag = flag + 1
                            reap = False
        return resultframe

    def __plot(self,dataframe : pd.DataFrame):
        dataframe.plot()
        plt.xlabel("Time(s)", size=18)# x軸指定

    def __create_netlist(self,netlist,config_data) -> str:
        # raw のリセット
        raw = ""
        # .print .endの行を取得
        for line in netlist.splitlines():
            
            print_obj = re.search('\.print',line, flags=re.IGNORECASE)
            end_obj = re.search('\.end$',line, flags=re.IGNORECASE)
            if not print_obj and not end_obj:
                raw = raw + line + "\n"

        if not config_data["phase.ele"]==[]:
            for ll in config_data["phase.ele"]:
                for l in ll:
                    raw = raw + ".print phase " + l + "\n"

        if not config_data["voltage.ele"]==[]:
            for ll in config_data["voltage.ele"]:
                for l in ll:
                    raw = raw + ".print devv " + l + "\n"

        raw = raw + ".end"
        return raw




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
    
 

def lll(flam):
    new = []
    tmp = 0
    for t in flam:
        if tmp == 0:
            tmp = t['time']
            p_tmp = t['phase']
            new.append(t)
        else:
            if tmp + 0.2e-09 > t['time']:
                continue
            else:
                tmp = t['time']
                p_tmp = p_tmp +1
                t['phase'] = p_tmp
                new.append(t)
    return new