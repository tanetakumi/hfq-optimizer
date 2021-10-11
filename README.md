# HFQ optimizer

## List

- dataframe
```
time     P(1)  P(2)   P(3)  P(4)
1.00e-5   .     .      .     .
1.01e-5   .     .      .     .
1.02e-5   .     .      .     .
.         .     .      .     .
```

- judge_squid
```
[{'1': 'P(1)', '2': 'P(2)'}, {'1': 'P(3)', '2': 'P(4)'}, {'1': 'P(5)', '2': 'P(6)'}]
```

- add list

```
time     P(1)+P(2)   P(3)+P(4)
1.00e-5      .           .
1.01e-5      .           .
1.02e-5      .           .
.            .           .
```

- start value
```
{'P(1)+P(2)' : num, 'P(3)+P(4)' : num}
```

- calulation

```
if (cross num+2pi or cross num-2pi):
    dict['P(1)+P(2)'] = num ± 2pi
    dataframe add time element phase
    
```
