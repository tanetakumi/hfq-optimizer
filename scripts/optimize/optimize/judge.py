import pandas as pd
import math
import re
import transitions
from .config import Config
import matplotlib.pyplot as plt
from .graph import sim_plot
from transitions import Machine

def get_switch_timing(config : Config, data : pd.DataFrame, plot = False) -> pd.DataFrame:

    p = math.pi
    p2 = math.pi * 2

    res_df = []

    if not config.phase_ele == []:
        new_df = pd.DataFrame()
        for squid in config.phase_ele:
            if len(squid) == 1:
                new_df['P('+'+'.join(squid)+')'] = data['P('+squid[0].upper()+')']
            elif len(squid) == 2:
                new_df['P('+'+'.join(squid)+')'] = data['P('+squid[0].upper()+')'] + data['P('+squid[1].upper()+')']
            elif len(squid) == 3:
                new_df['P('+'+'.join(squid)+')'] = data['P('+squid[0].upper()+')'] + data['P('+squid[1].upper()+')'] + data['P('+squid[2].upper()+')']
    
        if plot:
            sim_plot(new_df)

        for column_name, srs in new_df.items():
            # バイアスをかけた時の状態の位相(初期位相)
            init_phase = srs[( srs.index > config.start_time ) & ( srs.index < config.end_time )].mean()
            
            judge_phase = init_phase + p
            
            # クロックが入ってからのものを抽出
            srs = srs[srs.index > config.end_time]

            # 位相変数
            flag = 0
            for i in range(len(srs)-1):
                if (srs.iat[i] - (flag*p2 + judge_phase)) * (srs.iat[i+1] - (flag*p2 + judge_phase)) < 0:
                    flag = flag + 1
                    res_df.append({'time':srs.index[i], 'phase':flag, 'element':column_name})
                elif (srs.iat[i] - ((flag-1)*p2 + judge_phase)) * (srs.iat[i+1] - ((flag-1)*p2 + judge_phase)) < 0:
                    flag = flag - 1
                    res_df.append({'time':srs.index[i], 'phase':flag, 'element':column_name})

    if not config.voltage_ele == []:
        for vol in config.voltage_ele:
            srs_std = data['V('+vol+')'].rolling(window=10).std()
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
                        if srs_std_max.index[i] - tmp > config.pulse_interval/2:
                            res_df.append({'time':tmp, 'phase':flag, 'element':'V('+vol+')'})
                            res_df.append({'time':srs_std_max.index[i], 'phase':-flag, 'element':'V('+vol+')'})
                            flag = flag + 1
                        reap = False

    return res_df


def compare_switch_timings(dl1 : list, dl2 : list, config : Config) -> bool:

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
            if l2_time < l1_time - config.pulse_delay or l1_time + config.pulse_delay < l2_time:
                return False
        return True
    else:
        return False
    

def state_judgement(dl1 : list, config : Config) -> bool:

    #dict_listの中で一番最初のスイッチの記録(dict_list)を得る
    def first_switch(dict_list : list) -> list:
        #re_list=list()
        if len(dict_list)==0:
            raise ValueError("\033[31mNo switch.\033[0m")
        sw_t=list()
        for dl in dict_list:
            sw_t.append(dl['time'])
        indx=sw_t.index(min(sw_t))
        #re_list=dict_list[indx]
        return dict_list[indx]

    #dlの中のある素子の一番最初のスイッチ記録を削除する
    def delete_first_switch(dl : list, element : str):
        dl_t=list()
        sw_t=list()
        for l in dl:
            if l['element']==element:
                dl_t.append(l)
                sw_t.append(l['time'])
        indx=sw_t.index(min(sw_t))
        dl.remove(dl_t[indx])

    def search_output(dl : list, input_time : float, output_type : bool, output_ele : str, output_interval : float) -> bool:
        dl_t=list()
        sw_t=list()
        empty_flag=bool()
        earlest_sw_t=float()
        for l in dl:
            if l['element']==output_ele:
                dl_t.append(l)
                sw_t.append(l['time'])
        if len(sw_t)==0:
            empty_flag=True
        else:
            empty_flag=False
            earlest_sw_t=min(sw_t)
            indx=sw_t.index(earlest_sw_t)
            #確認したoutputは削除する
            dl.remove(dl_t[indx])
        if output_type:
            if empty_flag:
                return False
            if input_time<earlest_sw_t and earlest_sw_t<(input_time+output_interval):
                return True
            else:
                return False
        else:
            if input_time<earlest_sw_t and earlest_sw_t<(input_time+output_interval):
                return False
            if earlest_sw_t<input_time:
                return False
            if (input_time+output_interval)<earlest_sw_t or empty_flag:
                return True
            

    """
    @dataclass
    class transition_with_output:
        list_of_transition_w_output=list()
        list_of_transition_wo_output=list()
        #def __init__(list_of_transition : list):
    """
    
    class StateMachine(object):
        #初期化（ステートマシンの定義：とりうる状態の定義、初期状態の定義、各種遷移と紐付くアクションの定義）
        def __init__(self, name, list_of_state : list ,list_of_transition : list, initial_state : str):
            self.name = name
            self.output = False
            self.machine = Machine(model=self, states=list_of_state, initial=initial_state, auto_transitions=False)
            lt_temp=list()
            for lt in list_of_transition:
                trigger_temp=str()
                for squid in lt:
                    trigger_temp='P('+'+'.join(squid[0])+')'
                if len(lt)==3:
                    self.machine.add_transition(trigger_temp, source=lt[1],  dest=lt[2])
                if len(lt)==4:
                    self.machine.add_transition(trigger_temp, source=lt[1],  dest=lt[2], after=lt[3])
                else:
                    raise ValueError("\033[31mSize of [list_of_transition] is 3 or 4.\033[0m")

        #以下、遷移時のアクション
        def True_Output(self):
            self.output = True

        def False_Output(self):
            self.output = False


    SM=StateMachine('SM', config.list_of_state ,config.list_of_transition, config.initial_state)
    #now_state=config.initial_state

    #スイッチ記録をコピーして
    dl=dl1
    #elementフォーマット
    for squid in config.output_element:
        output_ele='P('+'+'.join(squid)+')'
    while True:
        #一番最初にスイッチした素子を探す
        switch_log=first_switch(dl)
        #対応する遷移があるか探す
        #無ければ例外が投げられるのでキャッチしてFalse終了
        try:
            SM.trigger(switch_log[0]['element'])
        except transitions.core.MachineError as e:
            return False
        #確認したスイッチ記録は削除する
        delete_first_switch(dl,switch_log[0]['element'])
        #outputを調べる
        if not search_output(dl, switch_log[0]['time'], SM.output, output_ele, config.output_interval):
            #Falseが戻ってきたらFalse終了
            return False
        #全てのスイッチ記録を確認したらbreak
        if len(dl)==0:
            break
    #全てクリアならTrue終了
    return True



    


