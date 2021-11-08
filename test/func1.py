import math
import scipy
from scipy import optimize
import numpy as np
import matplotlib.pyplot as plt

def f1(t2,phiex,n,licp):
    phi = 2.07*10**(-15)
    return 2*n*np.pi + 2*np.pi*phiex/phi + t2 - np.pi*licp*np.sin(t2)

def f3(t2,licp):
    return t2 - np.pi*licp*np.sin(t2)

def f2(t1,Y,licp):

    return t1 + np.pi*licp*np.sin(t1) -Y

def f2d(t1,Y,licp):

    return 1 + np.pi*licp*np.cos(t1) -Y




def Newton(t2,phiex,n,licp,init,err):
    x_n=init
    x_n_scc=0
    count=0
    Y=f1(t2,phiex,n,licp)
    print(Y)
    """
    while True:
        count=count+1
        x_n_scc=x_n-f2(x_n,Y,licp)/f2d(x_n,Y,licp)
        if np.abs(f2(x_n_scc,Y,licp))<err:
            break
        x_n=x_n_scc
        print(count,"   ",x_n_scc)"""

    print(\
        "数値解は",x_n_scc,\
        "\nその時の関数の値は",f2(x_n_scc,Y,licp),\
        "\n計算回数は",count,"です")    
    return x_n

    

if __name__ == "__main__":
    print(f3(np.pi*0.5,0.2))