from email.policy import default
import re
import pandas as pd
from .util import stringToNum, isfloat, isint
from .pyjosim import simulation
from .judge import judge, compareDataframe, operation_judge
from .util import vround
from .calculator import shunt_calc
import numpy as np

class Data:
    def __init__(self, raw_data : str, show : bool = False):
        self.vdf, self.sim_data = self.__get_variable(raw=raw_data)
        self.time_start= float(self.__get_value(raw_data, "EndTimeOfBiasRise"))
        self.time_stop = float(self.__get_value(raw_data, "StartTimeOfPulseInput"))
        self.squids = self.__get_judge_spuid(raw_data)
        self.default_result = pd.DataFrame()

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

    def __get_variable(self, raw : str) -> tuple:
        df = pd.DataFrame()
        
        vlist = re.findall('#.+\(.+?\)',raw)

        for raw_line in vlist:
            li = re.sub('\s','',raw_line)
            char = re.search('#.+?\(',li, flags=re.IGNORECASE).group()
            char = re.sub('#|\(','',char)
            if not df.empty and char in df['char'].tolist():
                continue
            dic = {'char': char,'def': None, 'main': None, 'sub': None, 'element':None,'fix': False,'shunt': None,'dp': True,'dpv': None,'tmp': 0}
            
            
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
                    break
            

            df = df.append(dic,ignore_index=True, verify_integrity=True)
        # dataframe の検査が必要かもしれない
        df.set_index('char', inplace=True)


        raw = re.sub('\*+\s*optimize[\s\S]+$','', raw)

        for v in re.findall('#.+\(.+?\)',raw):
            char = re.search('#.+?\(',v).group()
            char = re.sub('#|\(','',char)
            char = "#("+char+")"
            raw = raw.replace(v, char)
            
        return df , raw

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
                self.vdf.at[index,'sub'] = np.random.normal(tmp,tmp*dpv/200)

    def __get_value(self, raw, key) -> str:
        m_object = re.search(key+'=[\d\.\+e-]+', raw, flags=re.IGNORECASE)
        if m_object:
            return re.split('=', m_object.group())[1]
        else:
            return None

    def __get_judge_spuid(self, raw : str) -> list:
        squids = []
        tmp = []
        for line in raw.splitlines():
            m_obj = re.search('\.print\s+phase.+',line, flags=re.IGNORECASE)
            if m_obj:
                data_sub = re.sub('\s|\.print|phase','',m_obj.group(), flags=re.IGNORECASE)
                tmp.append('P('+data_sub+')')
            else:
                if len(tmp)>0:
                    squids.append(tmp)
                    tmp = []
        return squids

    def default_simulation(self,  plot = False):
        def_sim_data = self.sim_data
        # シュミレーションデータの作成
        for index in self.vdf.index:
            def_sim_data = def_sim_data.replace('#('+index+')', str(self.vdf.at[index, 'def']))
        
        print(def_sim_data)
        df = simulation(def_sim_data)
        if plot:
            print("default 値でのシュミレーション結果")
            df.plot()

        self.default_result = judge(self.time_start, self.time_stop, df, self.squids, plot)

    

