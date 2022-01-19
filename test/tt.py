import re

f = """
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


m_object = re.search("EndTimeOfBiasRise"+'=[\d\.\+e-]+', f, flags=re.IGNORECASE)
if m_object:
    print(m_object.group())
else:
    print("test")


squids = []
con = []
for line in f.splitlines():
    m_obj = re.search('\.print\s+phase.+',line, flags=re.IGNORECASE)
    if m_obj:
        data_sub = re.sub('\s|\.print|phase','',m_obj.group(), flags=re.IGNORECASE)
        con.append(data_sub)
    else:
        if len(con)>0:
            squids.append(con)
            con = []

print(squids)

"""
line = next(filter(lambda x: re.search(key, x), data.splitlines()),None)
if line is None:
    print(key + " の値が取得できません", file=sys.stderr)
    sys.exit(1)
else:
    r = re.split('=',line)
    if len(r) == 2:
        return r[1]
    else:
        print(key + " の値が取得できません", file=sys.stderr)
        sys.exit(1)"""