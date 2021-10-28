import pandas as pd
import matplotlib.pyplot as plt

if __name__ == '__main__':
    filepath = '/home/tanetakumi/main/hfq-optimizer/test/jtl_result.csv'
    vertical = 'L'
    horizontal = 'Vbias'
    
    df = pd.read_csv(filepath, header=0)

    for index, row in df.iterrows():
        if row['result']:
            plt.plot(row[horizontal], row[vertical],marker='.',linestyle='None',color = "Red")
        else:
            plt.plot(row[horizontal], row[vertical],marker='.',linestyle='None',color = "Blue")

    plt.show()

