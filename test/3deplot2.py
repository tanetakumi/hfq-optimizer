import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import random
import math

# Figureと3DAxeS
fig = plt.figure(figsize = (8, 8))
ax = fig.add_subplot(111, projection="3d")

# 軸ラベルを設定
ax.set_xlabel("A=Φex/Φ0", size = 16)
ax.set_ylabel("B=LIc/Φ0", size = 16)
ax.set_zlabel("Ig.max/Ic", size = 16)

# 円周率の定義
pi = np.pi

# (x,y)データを作成
x = np.linspace(0, 1, 50)
y = np.linspace(0, 1, 100)

def func(x,y,exphi,licphi):
    a = random.randint(0, 1)
    return a*2*math.cos(x)*math.sin(math.pi*(exphi-licphi*math.sin(x)*math.cos(y)))

resl = np.arange(5000,dtype=np.float64).reshape(50, 100)

for a in range(10):
    licp = a/10
    print(a)
    for b in range(50):
        ex = b/50
        vmax = 0
        for i in range(10000):
            t1 = random.random()*6.28
            t2 = random.random()*6.28
            res = func(t1,t2,ex,licp)
            if res > vmax:
                vmax = res

        resl[b][a] = vmax

# 格子点を作成
X, Y = np.meshgrid(x, y)

print(resl)

# 高度の計算式
#Z = np.cos(X/pi) * np.sin(Y/pi)
#print(type(Z))

# 曲面を描画
ax.plot_surface(X, Y, resl, cmap = "summer")

# 底面に等高線を描画
ax.contour(X, Y, resl, colors = "black", offset = -1)

plt.show()