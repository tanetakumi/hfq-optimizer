import re
from util import stringToNum

class Data:

    def __init__(self, raw_data : str, show : bool = False):
        # self.netlist = raw_data
        self.vlist = self.get_variable(raw_data)
        self.time_start = self.get_value(raw_data, "EndTimeOfBiasRise")
        self.time_stop = self.get_value(raw_data, "StartTimeOfPulseInput")
        self.squids = self.get_judge_spuid(raw_data)
        self.sim_data = re.sub('\*+\s*optimize[\s\S]+$','', raw_data)

        if show:
            print("--- List of variables to optimize ---")
            [print(v) for v in self.vlist]
            print("\n") 
            print("--- Period to calculate the initial value of bias ---")
            print(self.time_start, " ~ ", self.time_stop)
            print("\n")
            print("--- SQUID used for judging the operation ---")
            print(self.squids)
            print("\n")

    def get_variable(self, raw) -> list:
        vlist = []
        for line in re.findall('#.+\([\d\.]+\)', raw):
            #   # と ) を除く
            data = re.sub('#|\)','',line)

            #   (　で分割
            data_splited = re.split('\(', data)

            if re.search('@',data_splited[0]):
                data_dict = {'char': data_splited[0], 'text': line, 'def': stringToNum(data_splited[1]), 'fixed': True}
            else:
                data_dict = {'char': data_splited[0], 'text': line, 'def': stringToNum(data_splited[1]), 'fixed': False}

            if data_dict not in vlist:
                vlist.append(data_dict)
        return vlist

    def get_value(self, raw, key) -> str:
        m_object = re.search(key+'=[\d\.\+e-]+', raw, flags=re.IGNORECASE)
        if m_object:
            return float(re.split('=', m_object.group())[1])
        else:
            return None

    def get_judge_spuid(self, raw : str) -> list:
        squids = []
        tmp = []
        for line in raw.splitlines():
            m_obj = re.search('\.print\s+phase.+',line, flags=re.IGNORECASE)
            if m_obj:
                data_sub = re.sub('\s|\.print|phase','',m_obj.group(), flags=re.IGNORECASE)
                tmp.append(data_sub)
            else:
                if len(tmp)>0:
                    squids.append(tmp)
                    tmp = []
        return squids


if __name__ == "__main__":
    
    test_data = """
    .model jjmod jj(Rtype=1, Vg=2.8mV, Cap=0.064pF, R0=100ohm, Rn=16ohm, Icrit=0.1mA)
    .model pjjmod jj(Rtype=1, Vg=2.8mV, Cap=0.064pF, R0=100ohm, Rn=16ohm, Icrit=0.1mA, PHI=PI)

    *PYSQUID=========================================================================

    .subckt psquid        3  5 
    L1                 3         1   1.75pH fcheck
    L2                 3         4   1.75pH fcheck
    B1                 1         5  jjmod area=0.49
    R1                 1         5   15.88ohm
    B2                 2         5  jjmod area=0.49
    R2                 2         5   15.88ohm
    B3                 4         2  pjjmod area=20
    R3                 4         2   0.2ohm
    .ends
    *================================================================================


    .subckt HFQ_bias            1  3  4
    L1               1        2   20pH fcheck
    L2               2        3   20pH fcheck
    R1               2        4   130ohm
    .ends

    .subckt HFQ_bias_non        1  3  
    L1               1        2   20pH fcheck
    L2               2        3   20pH fcheck
    .ends


    .subckt DCHFQ 1 7 100
    Rin                     1        2    #DCHFQR1(150)ohm
    L0                      2        3    2pH fcheck
    L1                      3        0    #DCHFQL1(20)pH fcheck
    X1       psquid         3        4
    L3                      4        5    #DCHFQL2(4)pH fcheck
    L4                      5        6    2.00pH fcheck
    R1                      100      5    #DCHFQR2(100)ohm
    X2       psquid         6        0
    X3       JTL      6        7     100
    .ends

    .subckt DCHFQt 1 7 100
    Rin                     1        2    #DCHFQR1(150)ohm
    L0                      2        3    2pH fcheck
    L1                      3        0    #DCHFQL1(20)pH fcheck
    X1       psquid         3        4
    L3                      4        5    #DCHFQL2(4)pH fcheck
    L4                      5        6    2.00pH fcheck
    R1                      100      5    #DCHFQR2(100)ohm
    X2       psquid         6        0
    X3       JTL      6        7     100
    .ends


    .subckt JTL     1  5  100
    L1               1  2   #JTLL1(18)pH fcheck
    L2               2  3   #JTLL1(18)pH fcheck
    L3               3  4   #JTLL1(18)pH fcheck
    L4               4  5   #JTLL1(18)pH fcheck
    X1    psquid     3  0
    X2    psquid     5  0
    R1               100  4   #JTLR1(100)ohm
    .ends



    .subckt JTL4    1  5  100
    X1       JTL            1  2  100
    X2       JTL            2  3  100
    X3       JTL            3  4  100
    X4       JTL            4  5  100
    .ends


    .subckt DFF 1 4 9 100
    L1                   1  2  #DFFL1(10)pH fcheck  
    X1       psquid      2  3
    L2                   3  7  #DFFL2(18)pH fcheck

    L3                   4  5  #DFFL3(18)pH fcheck
    L4                   5  6  #DFFL4(18)pH fcheck
    X2       psquid      6  0
    L5                   6  7  2pH  fcheck
    R1                   100  7  #DFFR1(100)ohm
    L6                   7  8  #DFFL6(10)pH fcheck
    L7                   8  9  2pH fcheck
    X3       psquid      9  0
    .ends


    *** top cell: 
    Vin1                     1     0      PWL(0ps 0mV   360ps 0mV 370ps 25mV 470ps 25mV 480ps 0mV   860ps 0mV 870ps 25mV 970ps 25mV 980ps 0mV   1360ps 0mV 1370ps 25mV 1470ps 25mV 1480ps 0mV)
    X0       DCHFQt        1     2  100
    X1       JTL4          2     3  100
    X2       JTL4          3     4  100

    Vin2                     5     0      PWL(0ps 0mV   240ps 0mV 250ps 25mV 350ps 25mV 360ps 0mV   740ps 0mV 750ps 25mV 850ps 25mV 860ps 0mV   1240ps 0mV 1250ps 25mV 1350ps 25mV 1360ps 0mV)
    X3       DCHFQt        5     6  100
    X4       JTL4          6     7  100
    X5       JTL4          7     8  100

    X6       DFF           4     8  9 100
    X7       JTL4          9     10  100
    X8       JTL4          10    11  100


    X9       psquid        11     0
    R1                     11    12  8.32ohm
    L1                     12     0  2pH fcheck
    Vb                     100    0  pwl(0ps 0mV 100ps 1.2mV)



    **netlis file
    .tran 1.0ps 6000ps 0ps 1ps

    .print phase B1|X1|X1|X5
    .print phase B2|X1|X1|X5

    .print phase B1|X1|X1|X2
    .print phase B2|X1|X1|X2

    .print phase B1|X1|X1|X8
    .print phase B2|X1|X1|X8

    .end

    **** optimize ****
    * バイアス電圧の立ち上がり終了の時間
    * EndTimeOfBiasRise=100e-12
    * 初期パルスの入力開始時間
    * StartTimeOfPulseInput=200e-12
    
    """

    data = Data(test_data, True)

