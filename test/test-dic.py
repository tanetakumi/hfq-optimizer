var = {'cahr':'a','value':[1, 2, 3, 4, 5]}

print(var)


def createStrList(start,stop,step,digit) -> list:
    res = []
    value = start
    while(value<stop+step):
        res.append(str(round(value,digit)))
        value = value + step
    return res

if __name__ == '__main__':
    print(createStrList(1.8,3.5,0.1,1))
