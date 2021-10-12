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


def replace_value(input : str, path : str, data : pd.Series):
    new_file = input
    for index, value in data.iteritems():
        new_file = re.sub('#\('+index+'\)',value,new_file)

    with open(path+'/create.inp', mode="w") as f:
        f.write(new_file)

if __name__ == "__main__":

    colum = ['a','b']

    contents = [list(tup) for tup in itertools.product(*[['18','19'],['3','4','5']])]

    df = pd.DataFrame(contents,columns=colum)
    print(df)
    print(type(df.iloc[3]))
    print(df.iloc[3])
    # print(type(df[1]))
    #for column_name, srs in df.iterrows():
    #    print(srs)
    # series_3 = pd.Series([5,13], index=['a','b'])

    test_data = "hello\n this is test data\n replace this value\n You have #(a) apples\n iphone#(b)"
    # print(series_3)
    replace_value(test_data,os.path.dirname(__file__),df.iloc[3])