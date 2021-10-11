import itertools

A = ['x', 'y', 'z']
B = [1, 2, 3]
C = ['a', 'b', 'c']

D = []
D.append(A)
D.append(B)
D.append(C)


for tup in itertools.product(*D):
    print(list(tup))
print(list(itertools.product(*D)))
print(type(itertools.product(*D)))
print([list(tup) for tup in list(itertools.product(*D))])