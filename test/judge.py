import math
import pandas as pd
import sys
import os
    
def judge(data : pd.DataFrame, judge_squid : dict) -> pd.DataFrame:
    """  dataframe の形は
    time     P(1)  P(2)   P(3)  P(4)
    1.00e-5   .     .      .     .
    1.01e-5   .     .      .     .
    1.02e-5   .     .      .     .
    .         .     .      .     .
    """

    """  judge_squid の形は
    [{'1': 'P(1)', '2': 'P(2)'}, {'1': 'P(3)', '2': 'P(4)'}, {'1': 'P(5)', '2': 'P(6)'}]
    """

    p = math.pi *2
    newDataframe = pd.DataFrame()
    for di in judge_squid:
        newDataframe[di['1']+di['2']] = data[di['1']]+data[di['2']]
    print(newDataframe)

    print(p)

    resultframe = pd.DataFrame(columns=['time', 'element', 'phase'])
    # resultframe.set_index('time',inplace=True)

    for column_name, srs in newDataframe.iteritems():
        flag = 0
        for i in range(len(srs)-1):
            if (srs.iat[i] - (flag+1)*p) * (srs.iat[i+1] - (flag+1)*p) < 0:
                flag = flag + 1
                resultframe = resultframe.append({'time':srs.index[i], 'element':column_name, 'phase':flag},ignore_index=True)

            elif (srs.iat[i] - (flag-1)*p) * (srs.iat[i+1] - (flag-1)*p) < 0:
                flag = flag - 1
                resultframe = resultframe.append({'time':srs.index[i], 'element':column_name, 'phase':flag},ignore_index=True)

    resultframe.sort_values('time',inplace=True)
    resultframe.reset_index(drop=True,inplace=True)
    return resultframe
    #    for (i, index, item) in zip(range(len(srs)), srs.index, srs):
            

        # for index, item in srs.iteritems():
        #     print (index, item)


    """  return frame の形は
    time     element   phase   
    1.00e-5    P(1)      1      .     .
    2.53e-5    P(2)     -1      .     .
    4.72e-5    P(3)      1      .     .
    .           .        .      .     .
    """



if __name__ == '__main__':
    args = sys.argv
    if len(args) == 2:
        filepath = args[1]
        if os.path.exists(filepath):
            df = pd.read_csv(filepath,index_col=0)
            # print(df)
        else:
            print("ファイルが存在しません。\n指定されたパス:"+filepath)
    else:
        print("引数が足りません。\n入力された引数:"+str(len(args)))

    test=[{'1': 'P(B1|X2|X0)', '2': 'P(B2|X2|X0)'}, {'1': 'P(B1|X1|X1)', '2': 'P(B2|X1|X1)'}, {'1': 'P(B1|X1|X5)', '2': 'P(B2|X1|X5)'}]
    print(judge(df,test))