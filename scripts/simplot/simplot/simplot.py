import matplotlib.pyplot as plt
import os
import re
import sys
import io
from subprocess import PIPE
import subprocess
import pandas as pd

def check_lastline(data : str) -> str:
    return re.sub('\n*$','\n.end',data) if re.search('\.end\s*$', data) is None else data


def simulation(simulation_data : str) -> pd.DataFrame:
    simulation_data = check_lastline(simulation_data)
    result = subprocess.run(["josim-cli", "-i"], input=simulation_data, stdout=PIPE, stderr=PIPE, text=True)

    first_split = re.split('100%\s*Formatting\s*Output',result.stdout)
    if len(first_split) == 2:
        split_data = first_split[1]
    else:
        print("--- standard error ---")
        print("\033[31m" + result.stderr + "\033[0m")
        sys.exit()

    return pd.read_csv(io.StringIO(split_data),index_col=0,header=0, sep='\s+') if split_data is not None else None

def remove_opt_symbol(sim_data : str) -> str:
    # optimize の記述の削除したものの取得
    sim_data = re.sub('\*+\s*optimize\s*\*+[\s\S]+$','', sim_data)

    for s in re.findall('#.+\(.+\)',sim_data):
        value = re.sub('#.+\(|\)','',s)
        sim_data = sim_data.replace(s,value)
    
    return sim_data

def simulation_plot(filepath : str, savepath : str = None):
    if os.path.exists(filepath):
        # 読み込み
        with open(filepath, 'r') as f:
            raw = f.read()
        sim_data = remove_opt_symbol(raw)
        df = simulation(sim_data)
        df.plot()
        if filepath == None:
            plt.show()
        else:
            plt.savefig(savepath)
    else:
        print("ファイルが存在しません。\n指定されたパス:"+filepath,file=sys.stderr)
        sys.exit(1)

def main():
    if len(sys.argv) == 2:
        simulation_plot(sys.argv[1])
    elif len(sys.argv) == 3:
        simulation_plot(sys.argv[1],sys.argv[2])
    else:
        print("引数が足りません。\n入力された引数:"+str(len(sys.argv)),file=sys.stderr) 
        sys.exit(1)

