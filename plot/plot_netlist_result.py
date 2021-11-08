from typing import List
import matplotlib
from numpy import ldexp
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import os
import sys
import pandas as pd


def main(args : List):
    if len(args) == 2:
        filepath = args[1]
        if os.path.exists(filepath):
            df = pd.read_csv(filepath,index_col=0)
            print(df)
            df.plot()
            plt.show()
        else:
            print("ファイルが存在しません。\n指定されたパス:"+filepath)
    else:
        print("引数が足りません。\n入力された引数:"+str(len(args)))
    
    
if __name__ == '__main__':
    main(sys.argv)