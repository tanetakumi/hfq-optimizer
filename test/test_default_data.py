import pandas as pd

a = [{'char': 'a', 'default': 2.0, 'start': 1.8, 'stop': 1.9, 'step': 0.1, 'digit': 1}, {'char': 'b', 'default': 17, 'start': 10, 'stop': 30, 'step': 1, 'digit': 0}]

print(a)

b = [ i for i in a]

c = pd.Series(index=[ str(i['char']) for i in a], data=[ str(i['default']) for i in a ])

print(c)