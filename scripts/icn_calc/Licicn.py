import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def nominalic(L,ic):
    phizero=2.07e-15
    x = L * ic / phizero
    if x > 1.5:
        return np.nan
    else:
        return ( 0.5263*x**6 - 2.3279*x**5 + 3.4434*x**4 - 1.0023*x**3 - 2.5876*x**2 + 3.341*x ) * ic

# Figureと3DAxeS
fig = plt.figure(figsize = (8, 8))
ax = fig.add_subplot(111, projection="3d")

# 軸ラベルを設定
ax.set_xlabel("L [pH]", size = 18)
ax.set_ylabel("Ic [μA]", size = 18)
ax.set_zlabel("Icn [μA]", size = 18)

x_size = 200
y_size = 100
# (x,y)データを作成
x = np.linspace(1e-12, 50e-12, x_size)
y = np.linspace(30e-6, 100e-6, y_size)

# 格子点を作成
X, Y = np.meshgrid(x, y)

# Z = nominalic(X, Y)
Z = np.empty((y_size, x_size), dtype=float)
# print(Z)


for yn in range(y_size):
    for xn in range(x_size):
        Z[yn][xn] = nominalic(x[xn],y[yn])


X = X/1e-12
Y = Y/1e-6
Z = Z/1e-6
ax.plot_wireframe(X, Y, Z)
plt.tick_params(labelsize=14)
plt.show()

# 曲面を描画
# ax.plot_surface(X, Y, Z, cmap = "plasma_r")

# 底面に等高線を描画
# ax.contour(X, Y, Z, colors = "silver", offset = 0)

# plt.show()




"""
# Figureを追加
fig = plt.figure(figsize = (8, 8))

# 3DAxesを追加
ax = fig.add_subplot(111, projection='3d')

# Axesのタイトルを設定
ax.set_title("Helix", size = 20)

# 軸ラベルを設定
ax.set_xlabel("x", size = 14)
ax.set_ylabel("y", size = 14)
ax.set_zlabel("z", size = 14)

# 軸目盛を設定
#ax.set_xticks([-1.0, -0.5, 0.0, 0.5, 1.0])
#ax.set_yticks([-1.0, -0.5, 0.0, 0.5, 1.0])

# 円周率の定義
pi = np.pi

# パラメータ分割数
n = 256

# パラメータtを作成
t = np.linspace(-6*pi, 6*pi, n)

# らせんの方程式
x = np.cos(t)
y = np.sin(t)
z = t

# 曲線を描画
ax.plot(x, y, z, color = "red")

plt.show()

"""
