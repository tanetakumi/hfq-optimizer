import pandas as pd
import re

def order(filepath : str, index_list : list, bias : str):
    df = pd.read_csv(filepath, header=0)
    df = df[df['result']!=False]

    new = pd.DataFrame()

    for name, group in df.groupby(index_list):
        dict = {str(tuple(index_list)) : str(name)}
        dict["count"]=len(group)
        dict["Vbias"]=str(sorted(group[bias].values.tolist()))
        record = pd.Series(dict)
        new = new.append(record, ignore_index=True)

    new.sort_values("count",inplace=True)
    new.reset_index(inplace=True,drop=True)
    new.to_csv(filepath.replace('.','_order.'), mode='w',index= False)

if __name__ == '__main__':

    index_list = ["A","L"]
    bias = "Vbias"
    filepath = "/home/tanetakumi/main/hfq-optimizer/result/hfq-jtl/a2.csv"

    order(filepath,index_list,bias)
    # print(df)

