import numpy as np
import math
import random

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
        max_y = 0
        for i in range(10000):
            y = random.random()*1.6
            result = func3(y,A,B)
            if result > vmax:
                vmax = result
                max_y = y
        print(B, ", ", max_y)
        return vmax

def igic(x: float, licphi: float, exphi: float):
    if licphi < 1.0e-7:
        return 2*math.cos(exphi*math.pi)
    if x < 1.0e-7:
        return 0
    else:
        tmp1 = 2*(x - exphi * math.pi)/(licphi * math.pi)
        tmp2 = (tmp1**2) * (1/(math.tan(x)**2))
        tmp3 = 4 * math.cos(x)**2 - tmp2
        if tmp3 < 0:
            return 0
        else:
            return math.sqrt(tmp3)

def igic_max(licphi: float, exphi: float, accuracy: int = 1000):
    max = 0
    for i in range(1,accuracy):
        x = (i/accuracy)*math.pi *2
        val = igic(x, licphi, exphi)
        if val > max:
            max = val
    return max
