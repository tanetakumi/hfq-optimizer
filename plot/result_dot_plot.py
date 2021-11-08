import pandas as pd
import matplotlib.pyplot as plt

if __name__ == '__main__':
    f = [
        '/home/tane/main/hfq-optimizer/result/lval2.csv', '/home/tane/main/hfq-optimizer/result/lval3.csv'
    ]
    vertical = 'L'
    horizontal = 'Vbias'
    
    

    for filepath in f:
        print(filepath)
        df = pd.read_csv(filepath, header=0)
        for index, row in df.iterrows():
            if row['result']:
                plt.plot(row[horizontal], row[vertical],marker='.',linestyle='None',color = "Red")
            else:
                plt.plot(row[horizontal], row[vertical],marker='.',linestyle='None',color = "Blue")
    plt.show()

