import matplotlib.pyplot as plt
import numpy as np
import math
import random 

def func(t1,t2,licp):
    a = (t1+t2)/2
    b = (t1-t2)/2
    p = math.pi
    return 2* np.cos(a) * np.sin(-1*p*licp*np.sin(a)*np.cos(b))

if __name__ == "__main__":

    for j in range(1000):
        licp = j/1000
        vmin = 0
        for i in range(10000):
            t1 = random.random()*6.28
            t2 = random.random()*6.28
            res = func(t1,t2,licp)
            if res > vmin:
                vmin = res
        print(licp)
        plt.plot(licp, vmin ,marker='.',linestyle='None',color = "Blue")
    plt.show()