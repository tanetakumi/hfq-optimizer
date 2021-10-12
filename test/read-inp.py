import csv
import re
import itertools
import os
import sys
import pandas as pd
import subprocess
from subprocess import PIPE
import io
import numpy as np
import math
        
def isint(s):  # 正規表現を使って判定を行う
    p = '[-+]?\d+'
    return True if re.fullmatch(p, s) else False

def isfloat(s):  # 正規表現を使って判定を行う
    p = '[-+]?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?'
    return True if re.fullmatch(p, s) else False

def digit(s):  # 正規表現を使って小数点以下の桁数
    if re.search("\.",s)!= None:
        return len(re.split("\.",s)[1])
    else:
        return 0

def get_variable(input : str) -> list:

    # 変数の前につける先頭文字(正規表現)
    lead_str = '\*v\*'

    var = []

    for l in input.splitlines():
        if re.search(lead_str,l) != None:
            subdata = re.sub('#|\(|\)|\s|'+lead_str,'',l)
            # print(subdata)
            spldata = re.split("=|;",subdata)
            if len(spldata) == 5:
                di = digit(spldata[4])
                for i in range(1,5):
                    if isint(spldata[i]):
                        # print("int")
                        spldata[i] = int(spldata[i])
                    elif isfloat(spldata[i]):
                        # print("float")
                        spldata[i] = float(spldata[i])
                    else:
                        print("数値変換ができません。")
                        print(l)
                        sys.exit()
                vv = {"char":spldata[0], "default":spldata[1], "start":spldata[2], "stop":spldata[3], "step":spldata[4], "digit":di}
                var.append(vv)
            else:
                print("\033[31m変数の書き方が間違っています。\033[0m")
                print(lead_str+"<変数>=(<default>;<start>;<stop>;<step>)")
                sys.exit()
    # 取得結果の表示
    print(var)
    return var

def get_judge_spuid(input : str) -> list:
    squids = []
    # 改行が一回だけ、すなわち連続されて記述されている(.print phase <要素>)の部分を取得
    for m in re.finditer('\.print\s+phase.+\n.*\.print\s+phase\s+.+',input):
        rawdata = m.group()
        subdata = re.sub('[\t\f\v ]|\.print\s+phase','',rawdata)
        spldata = re.split("\n",subdata)
        if len(spldata) == 2:
            squids.append({"1" : "P("+spldata[0]+")", "2" : "P("+spldata[1]+")"})
        else:
            print("ERROR")
            print(rawdata)
            print(subdata)
            sys.exit()
    # 取得結果の表示 
    print(squids)
    return squids


def mkNumList(start,stop,step,digit) -> list:
    res = []
    value = start
    while(value<stop+step):
        res.append(str(round(value,digit)))
        value = value + step
    return res

def cut_josim_data(raw : str) -> str:
    first_split = raw.split('100% Formatting Output')

    if len(first_split) == 2:
        return first_split[1]
    else:
        print("\033[31m[ERROR] シュミレーションされませんでした。\033[0m")
        print(raw)
        sys.exit()

def simulation(simulator_path : str, simulation_dir : str, num : str, inp_data : str, var : pd.DataFrame, judge_squid : list) -> pd.DataFrame:

    return_list = []

    simulation_file = simulation_dir + "/sim" + num + ".inp"

    var['result'] = np.NaN
    
    for index_df, row in var.iterrows():
        new_file = inp_data
        for index_se, value in row.items():
            if index_se != 'result':
                new_file = re.sub('#\('+index_se+'\)',value,new_file)
        
        with open(simulation_file, mode="w") as f:
            f.write(new_file)
            
        result = subprocess.run([simulator_path, simulation_file,"-V", "1"], stdout=PIPE, stderr=PIPE, text=True)
        split_data = cut_josim_data(result.stdout)
        result_data = pd.read_csv(io.StringIO(split_data),index_col=0,header=0)

        for d in judge_squid:
            print("Hwllo")
        # judge = judge_frame(result_data)
        # row['result'] = judge()

    os.remove(simulation_file)
    print("thread"+num+":complete")
    return var


def judge(data : pd.DataFrame, judge_squid : dict) -> pd.DataFrame:

    p = math.pi *2

    newDataframe = pd.DataFrame()
    for di in judge_squid:
        newDataframe[di['1']+di['2']] = data[di['1']]+data[di['2']]
    # print(newDataframe)

    resultframe = pd.DataFrame(columns=['time', 'element', 'phase'])
    for column_name, srs in newDataframe.iteritems():
        flag = 0
        for i in range(len(srs)-1):
            if (srs.iat[i] - (flag+1)*p) * (srs.iat[i+1] - (flag+1)*p) < 0:
                flag = flag + 1
                resultframe = resultframe.append({'time':srs.index[i], 'element':column_name, 'phase':flag},ignore_index=True)

            elif (srs.iat[i] - (flag-1)*p) * (srs.iat[i+1] - (flag-1)*p) < 0:
                flag = flag - 1
                resultframe = resultframe.append({'time':srs.index[i], 'element':column_name, 'phase':flag},ignore_index=True)

    resultframe.sort_values('time',inplace=True)
    resultframe.reset_index(drop=True,inplace=True)
    return resultframe
    
    

    




if __name__ == '__main__':
    print('getcwd:      ', os.getcwd())
    print('dirname:     ', os.path.dirname(__file__))
    
    dir = os.path.dirname(__file__)

    with open(dir+'/test.inp','r') as f:
        raw = f.read()

    # 変数部分取得
    variables = get_variable(raw)
    # 判定するSQUID部分取得
    squids = get_judge_spuid(raw)
    # 変数辞書->リスト変換
    vlist = []
    for v in variables:
        vlist.append({'char':v['char'],'value':mkNumList(v['start'],v['stop'],v['step'],v['digit'])})
    
    

    colum = [d.get('char') for d in vlist]

    contents = [list(tup) for tup in itertools.product(*[d.get('value') for d in vlist])]

    df = pd.DataFrame(contents,columns=colum)

    print("-------------------------------------------")
    print(df)
    print("-------------------------------------------")


    df['result'] = np.nan

    # judge(sim_result,squids)
    # print(df)
    


        

    # print(df)


"""
    new_file = raw
    for v in variables:
        new_file = re.sub('#\('+v['char']+'\)',str(v['start']),new_file)

    with open(dir+'/create.inp', mode="w") as f:
        f.write(new_file)
"""



"""
for m in re.finditer('#\(\w+\)',hole):
    data = m.group()
    print(data)"""

# print(hole)
"""
for m in re.finditer('#\(.*\)',hole):
    data = m.group()
    data_list = re.split(';',re.sub('#|\(|\)','',data))
    """
    # print(makelist(data_list))
    

# with open('test2.inp', mode='w') as f:
#     f.write(hole)



# #(2.7;3.5;0.1)