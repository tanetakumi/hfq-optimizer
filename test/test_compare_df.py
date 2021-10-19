import pandas as pd

#, columns=["time","element","phase"]



def compareDataframe(df1 : pd.DataFrame, df2 : pd.DataFrame):
    return df1.drop('time', axis=1).equals(df2.drop('time', axis=1))

if __name__ == "__main__":

    a = pd.DataFrame(data = {"time":[1.00e-10,2.25e-10],"element":["P(A)","P(B)"],"phase":[1, -1]})

    b = pd.DataFrame(data = {"time":[1.05e-10,2.30e-10],"element":["P(A)","P(B)"],"phase":[1, -1]})
    print(compareDataframe(a,b))