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

if __name__ == "__main__":
    L = 3.5 * 10**(-12)
    Ic = 0.0001
    phi = 2.07 * 10 ** (-15)
    result = func_igmax(0, (L*Ic)/phi)
    print("nominal ic")        
    print('{:.8f}'.format(result*Ic))
