import re
import pandas as pd
from .util import stringToNum, isfloat, isint
from .pyjosim import simulation
from .judge import judge, compareDataframe

class Data:
    def __init__(self, raw_data : str, show : bool = False):
        self.v_df, self.sim_data = self.__get_variable(raw=raw_data)
        self.time_start = float(self.__get_value(raw_data, "EndTimeOfBiasRise"))
        self.time_stop = float(self.__get_value(raw_data, "StartTimeOfPulseInput"))
        self.squids = self.__get_judge_spuid(raw_data)
        self.default_result = pd.DataFrame()

        if show:
            print("--- List of variables to optimize ---")
            print(self.v_df)
            print('\n')
            print("--- Period to calculate the initial value of bias ---")
            print(self.time_start, " ~ ", self.time_stop)
            print('\n')
            print("--- SQUID used for judging the operation ---")
            print(self.squids)
            print('\n')

    def __get_variable(self, raw : str) -> tuple:
        df = pd.DataFrame(columns=['char','default','value','element','fix','lic','bc','global'])  
        df.set_index('char', inplace=True)
        vlist = re.findall('#.+\(.+\)',raw)

        for raw_line in vlist:
            li = re.sub('\s','',raw_line)
            char = re.search('#.+\(',li, flags=re.IGNORECASE).group()
            char = re.sub('#|\(','',char)
            if char in df.index:
                continue
            
            dic = {'default': None,'value': None,'element':None,'fix': False,'lic': None,'bc': None,'global': None}
            m = re.search('\(.+\)',li).group()
            m = re.sub('\(|\)','',m)
            spl = re.split(',',m)
            if len(spl)==1:
                if isfloat(spl[0]) or isint(spl[0]):
                    num = stringToNum(spl[0])
                    dic['default'] = num
                    dic['value'] = num
            for sp in spl:
                val = re.split('=',sp)
                if len(val) == 1:
                    if isfloat(val[0]) or isint(val[0]):
                        num = stringToNum(spl[0])
                        dic['default'] = num
                        dic['value'] = num
                elif len(val) == 2:
                    if re.fullmatch('v|value',val[0],flags=re.IGNORECASE):
                        num = stringToNum(val[1])
                        dic['default'] = num
                        dic['value'] = num
                    elif re.fullmatch('fix|fixed',val[0],flags=re.IGNORECASE):
                        if re.fullmatch('true',val[1],flags=re.IGNORECASE):
                            dic['fix'] = True
                        else:
                            dic['fix'] = False
                    elif re.fullmatch('lic',val[0],flags=re.IGNORECASE):
                        dic['lic'] = val[1]
                        # if re.fullmatch('(L|Ic|I)\d+',val[1],flags=re.IGNORECASE):
                        #     dic['lic'] = val[1]
                        # else:
                        #     raise ValueError("[ "+sp+" ]のLIc積の記述が読み取れません。")
                    elif re.fullmatch('(β|b)c',val[0],flags=re.IGNORECASE):
                        dic['bc'] = val[1]
                        # if re.fullmatch('(A|R)\d+',val[1],flags=re.IGNORECASE):
                        #     dic['bc'] = val[1]
                        # else:
                        #     raise ValueError("[ "+sp+" ]のbcの記述が読み取れません。")
                    elif re.fullmatch('global',val[0],flags=re.IGNORECASE):
                        num = stringToNum(val[1])
                        dic['global'] = num
                    else:
                        raise ValueError("[ "+sp+" ]の記述が読み取れません。")
                else:
                    raise ValueError("[ "+sp+" ]の記述が読み取れません。")
            
            # if dic['global'] == None:
            for line in raw.splitlines():
                if raw_line in line:
                    if re.fullmatch('R',line[0:1],flags=re.IGNORECASE):
                        dic['element'] = 'R'
                        if dic['global'] == None:
                            dic['global'] = 8
                    elif re.fullmatch('L',line[0:1],flags=re.IGNORECASE):
                        dic['element'] = 'L'
                        if dic['global'] == None:
                            dic['global'] = 9
                    elif re.fullmatch('C',line[0:1],flags=re.IGNORECASE):
                        dic['element'] = 'C'
                        if dic['global'] == None:
                            dic['global'] = 5
                    elif re.fullmatch('V',line[0:1],flags=re.IGNORECASE):
                        dic['element'] = 'V'
                        if dic['global'] == None:
                            dic['global'] = 5
                    elif re.fullmatch('B',line[0:1],flags=re.IGNORECASE):
                        dic['element'] = 'B'
                        if dic['global'] == None:
                            dic['global'] = 5
                    break
            
            df.loc[char] = dic
        # dataframe の検査が必要かもしれない
        
        raw = re.sub('\*+\s*optimize[\s\S]+$','', raw)

        for v in re.findall('#.+\(.+\)',raw):
            char = re.search('#.+\(',v).group()
            char = re.sub('#|\(','',char)
            char = "#("+char+")"
            raw = raw.replace(v, char)
            
        return df , raw

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
        # すべてdefault value に置き換えてjudge
        for index, row in self.v_df.iterrows():            
            def_sim_data = def_sim_data.replace("#("+index+")", str(row['value']))
        
        df = simulation(def_sim_data)
        if plot:
            print("default 値でのシュミレーション結果")
            df.plot()

        self.default_result = judge(self.time_start, self.time_stop, df, self.squids, plot)

    def test_simulation(self, plot= False):
        tmp_sim_data = self.sim_data
        # すべてdefault value に置き換えてjudge
        for index, row in self.v_df.iterrows():            
            tmp_sim_data = tmp_sim_data.replace("#("+index+")", str(row['value']))
        # 動作したか確認
        result_df = judge(self.time_start, self.time_stop, simulation(tmp_sim_data), self.squids)
        return compareDataframe(result_df, self.default_result)
    
    def test_simulation(self, plot= False):
        tmp_sim_data = self.sim_data
        # すべてdefault value に置き換えてjudge
        for index, row in self.v_df.iterrows():            
            tmp_sim_data = tmp_sim_data.replace("#("+index+")", str(row['value']))
        # 動作したか確認
        result_df = judge(self.time_start, self.time_stop, simulation(tmp_sim_data), self.squids)
        return compareDataframe(result_df, self.default_result)
        
