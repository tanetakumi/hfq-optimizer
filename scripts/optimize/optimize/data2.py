import re
import pandas as pd
from .util import stringToNum
from .pyjosim import simulation
from .judge import judge

class Data:
    def __init__(self, raw_data : str, show : bool = False):
        self.v_df = self.get_variable(raw_data)
        self.time_start = float(self.get_value(raw_data, "EndTimeOfBiasRise"))
        self.time_stop = float(self.get_value(raw_data, "StartTimeOfPulseInput"))
        self.squids = self.get_judge_spuid(raw_data)
        self.sim_data = re.sub('\*+\s*optimize[\s\S]+$','', raw_data)
        self.default_result = None

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

    def get_variable(self, raw) -> list:
        df = pd.DataFrame(columns=['char', 'default', 'value', 'fixed', 'text'])
        df.set_index('char', inplace=True)

        for line in re.findall('#.+\([\d\.]+\)', raw):
            #   # と ) を除く
            data = re.sub('#|\)','',line)

            #   (　で分割
            data_splited = re.split('\(', data)
            
            # ERROR処理を入れるべきである --------------------------------------
            # char の値と text の値がどちらか競合していた時
            #
            # ----------------------------------------------------------------
            if data_splited[0] not in df.index.values:
                if re.search('@',data_splited[0]):
                    df.loc[data_splited[0]] = (stringToNum(data_splited[1]), stringToNum(data_splited[1]), True, line)
                else:
                    df.loc[data_splited[0]] = (stringToNum(data_splited[1]), stringToNum(data_splited[1]), False, line)

        return df

    def get_value(self, raw, key) -> str:
        m_object = re.search(key+'=[\d\.\+e-]+', raw, flags=re.IGNORECASE)
        if m_object:
            return re.split('=', m_object.group())[1]
        else:
            return None

    def get_judge_spuid(self, raw : str) -> list:
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
            def_sim_data = def_sim_data.replace(row['text'], str(row['default']))
        
        df = simulation(def_sim_data)
        if plot:
            print("default 値でのシュミレーション結果")
            df.plot()
        res = judge(self.time_start, self.time_stop, df, self.squids)
        print(res)
        
