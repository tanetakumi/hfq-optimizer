import pandas as pd
 
resultframe = pd.DataFrame(columns=['time', 'element', 'phase'])
# resultframe.set_index('time',inplace=True)
 
data = {'time' : '鈴木次郎', 'element' : '男', 'phase' : 23}
df_new = resultframe.append(data, ignore_index=True)
df_new.set_index('time',inplace=True)
print(df_new)