import numpy as np
import random
import math
a = np.arange(100,dtype=np.float64).reshape(10, 10)




def func(x,y,exphi,licphi):
    a = random.randint(0, 1)
    return a*2*math.cos(x)*math.sin(math.pi*(exphi-licphi*math.sin(x)*math.cos(y)))

resl = np.arange(5000,dtype=np.float64).reshape(50, 100)

for a in range(100):
    licp = a/100
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
        print(res[4][5])
        res[b:a] = vmax