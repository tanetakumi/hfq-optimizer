import numpy as np
import math
import random 

t1 = [i/100 for i in range(628)]
t2 = [i/100 for i in range(628)]

def func(t1,t2,licp):
    a = (t1+t2)/2
    b = (t1-t2)/2
    p = math.pi
    return 2* np.cos(a) * np.sin(-1*p*licp*np.sin(a)*np.cos(b))

if __name__ == "__main__":
    L = 3.5 * 10**(-12)
    Ic = 0.0001
    phi = 2.07 * 10 ** (-15)
    vmin = 0
    for i in range(10000):
        t1 = random.random()*6.28
        t2 = random.random()*6.28
        res = func(t1,t2,L*Ic/phi)
        if res > vmin:
            vmin = res
    print(vmin*Ic)