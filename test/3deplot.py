import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import random

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
x = np.linspace(-2, 2, 400)
y = np.linspace(0, 1, 100)

# 格子点を作成
X, Y = np.meshgrid(x, y)

# 高度の計算式
Z = np.cos(X/pi) * np.sin(Y/pi)
print(type(Z))

# 曲面を描画
ax.plot_surface(X, Y, Z, cmap = "summer")

# 底面に等高線を描画
ax.contour(X, Y, Z, colors = "black", offset = -1)

plt.show()