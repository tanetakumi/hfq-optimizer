import numpy as np
import math
import random


def func(t1,t2,licp,ex):
    p =  math.pi
    return t1 + p*licp*math.sin(t1) + p*licp*math.sin(t2) - t2 - 2 * p * ex

if __name__ == "__main__":
    print(random.randint(0,1))