import pandas as pd




def split_dataframe(df, k):
    dfs = [df.loc[i:i+k-1, :] for i in range(0, len(df), k)]
    return dfs

if __name__ == "__main__":
    df = pd.DataFrame(data = {'a':[1,4,6,8,12,34,336,82], 'b':[8,93,75,20,18,344,56,543], 'c':[4,7,32,65,122,324,6,852]})
    dfs =  split_dataframe(df,2)
    for i, d in enumerate(dfs):
        print(i)
        print(d)

        d.to_csv('./out_a.csv', mode='a', header=False, index=False)