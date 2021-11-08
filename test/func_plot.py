import matplotlib.pyplot as plt
import numpy as np
import math

p = np.linspace( -20, 20, 10000)   # linspace(min, max, N) で範囲 min から max を N 分割します

q = p + np.sin(p)

print(q)
plt.plot(p, q)
plt.show()