import matplotlib.pyplot as plt
import numpy as np
import math
import random 

def func(x,y,exphi,licphi):
    a = random.randint(0, 1)
    return a*2*math.cos(x)*math.sin(math.pi*(exphi-licphi*math.sin(x)*math.cos(y)))

if __name__ == "__main__":
    for a in range(100):
        licp = a/100
        for b in range(50):
            ex = b/50
            vmin = 0
            for i in range(10000):
                t1 = random.random()*6.28
                t2 = random.random()*6.28
                res = func(t1,t2,ex,licp)
                if res > vmin:
                    vmin = res

            plt.plot(ex, vmin ,marker='.',linestyle='None',color = "Blue")
    plt.show()