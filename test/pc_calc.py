
import re
import os
import sys
from matplotlib.pyplot import plot
import pandas as pd
import subprocess
from subprocess import PIPE
import io
import math
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt


def get_judge_registance(input : str) ->tuple:
    registance = []
    raw = input
    # 改行が一回だけ、すなわち連続されて記述されている(.print phase <要素>)の部分を取得
    for m in re.finditer('\.print\s+devw\s+.+\n',input,re.IGNORECASE):
        rawdata = m.group()
        # print(rawdata)
        subdata = re.sub('\s|.print|devw|DEVW|\*','',rawdata)
        # print(subdata)
        raw = raw.replace(rawdata,'.print DEVV '+subdata+'\n.print DEVI '+subdata+'\n')
        registance.append(subdata)
    return registance, raw


def cut_josim_data(raw : str) -> str:
    first_split = raw.split('100% Formatting Output')

    if len(first_split) == 2:
        return first_split[1]
    else:
        print("\033[31m[ERROR] シュミレーションされませんでした。\033[0m")
        print(raw)
        sys.exit()



def judge(data : pd.DataFrame, judge_squid : list) -> pd.DataFrame:

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
    

def simulation(input : str, data : pd.Series, filepath : str) -> pd.DataFrame:
    new_file = input
    for index, value in data.iteritems():
        new_file = re.sub('#\('+index+'\)',value,new_file)
    
    with open(filepath, mode="w") as f:
        f.write(new_file)

    result = subprocess.run(["josim-cli", filepath, "-V", "1"], stdout=PIPE, stderr=PIPE, text=True)
    split_data = cut_josim_data(result.stdout)
    return pd.read_csv(io.StringIO(split_data),index_col=0,header=0)



    
        

def get_default_data(input : str, filepath : str, dic_data : list, judge_squid : list) -> pd.DataFrame:
    print("Simulation of default value")

    srs = pd.Series(index=[ str(d['char']) for d in dic_data ], data=[ str(d['default']) for d in dic_data ])
    result = simulation(input, srs, filepath)
    os.remove(filepath)
    return judge(result,judge_squid)


def compareDataframe(df1 : pd.DataFrame, df2 : pd.DataFrame) -> bool:
    return df1.drop('time', axis=1).equals(df2.drop('time', axis=1))


def split_dataframe(df, k):
    dfs = [df.loc[i:i+k-1, :] for i in range(0, len(df), k)]
    return dfs




# 引数で入力するのは　python optimizer.py simulation_file output_file
if __name__ == '__main__':
    dir = os.getcwd()
    filepath = dir + "/tmp_pc_calc.inp"

    print('\033[31mcurrent dir:\t\t\033[0m', dir)
    print('\033[31mdir of this py program:\t\033[0m', os.path.dirname(__file__))

    # confirm argument --------------------------
    if len(sys.argv) != 2:
        print("\033[31m[ERROR]\033[0m Wrong number of arguments for the function.")
        sys.exit()

    if os.path.exists(sys.argv[1]):
        print("\033[31msimulation file:\033[0m\t",sys.argv[1])
    else:
        print("\033[31m[ERROR]\033[0m file not exist:\t",sys.argv[1])
        sys.exit()

    # confirm argument --------------------------

    # 読み込み
    with open(sys.argv[1],'r') as f:
        raw = f.read()

    
    # 判定するSQUID部分取得
    tup = get_judge_registance(raw)
    print(tup[0])
    print(tup[1])

    with open(filepath, mode="w") as f:
        f.write(tup[1])

    
    result = subprocess.run(["josim-cli", filepath, "-V", "1"], stdout=PIPE, stderr=PIPE, text=True)
    split_data = cut_josim_data(result.stdout)
    df = pd.read_csv(io.StringIO(split_data),index_col=0,header=0)
    # print(df.index)
    print(df)
    new_df = pd.DataFrame(index=df.index,columns=[])
    print(tup[0])
    for w in tup[0]:
        w = w.upper()
        new_df['W('+w+')'] = df['V('+w+')'] * df['I('+w+')']
    print(new_df)

    os.remove(filepath)

    new_df.plot()
    plt.show()