import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import random
import math



# A = 外部磁場　B = LIc
def func(y,A,B):
    p = math.pi
    n = random.randint(0,1)
    mi = 1-((p*(n-A)-y)/(p*B*math.cos(y)))**2
    if mi > 0:
        return math.sqrt(mi)*2*math.sin(y)
    else:
        return 0

# A = 外部磁場　B = LIc
def func2(y,A,B):
    p = math.pi
    n = random.randint(0,1)
    mi = 1-((y-p*A)/(p*B*math.cos(y)))**2
    return math.sqrt(mi)*2*math.fabs(math.sin(y))

# A = 外部磁場　B = LIc
def func3(y,A,B):
    p = math.pi
    n = random.randint(-3,3)
    mi = (y-p*A+n*p)/(p*B*math.cos(y))
    if mi >-1 and mi < 1:
        x = math.asin(mi)
        return 2* math.cos(x)*math.sin(y)
    else: 
        return 0

# A = 外部磁場　B = LIc
def func_igmax(A,B):
    if B == 0:
        return math.fabs(2*math.sin(A*math.pi))
    else:    
        vmax = 0
        for i in range(3000):
            y = (random.random()-0.5)*2*6.28
            result = func3(y,A,B)
            if result > vmax:
                vmax = result
        return vmax




if __name__ == "__main__":
    # Figureと3DAxeS
    fig = plt.figure(figsize = (8, 8))
    ax = fig.add_subplot(111, projection="3d")

    # 軸ラベルを設定
    ax.set_xlabel("B=LIc/Φ0", size = 16)
    ax.set_ylabel("A=Φex/Φ0", size = 16)
    ax.set_zlabel("Ig.max/Ic", size = 16)

    # 円周率の定義
    pi = np.pi

    licp_ax=50
    ex_ax=300

    # (x,y)データを作成
    x = np.linspace(0, 1, licp_ax)
    y = np.linspace(-3, 3, ex_ax)


    # 格子点を作成
    X, Y = np.meshgrid(x, y)
    
    # X, Y は逆向き
    Z = np.empty([ex_ax, licp_ax], dtype=float)
    

    for _x in range(licp_ax):
        licp = _x/licp_ax
        print(_x)
        for _y in range(ex_ax):
            ex = (_y-150)/50
            Z[_y][_x] = func_igmax(ex,licp)
    
    # 曲面を描画
    ax.plot_surface(X, Y, Z, cmap = "plasma_r")

    # 底面に等高線を描画
    ax.contour(X, Y, Z, colors = "silver", offset = 0)
    
    plt.show()