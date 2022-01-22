import re

def isint(s):  # 正規表現を使って判定を行う
    p = '[-+]?\d+'
    return True if re.fullmatch(p, s) else False

def isfloat(s):  # 正規表現を使って判定を行う
    p = '[-+]?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?'
    return True if re.fullmatch(p, s) else False

def digit(s):  # 正規表現を使って小数点以下の桁数
    if re.search("\.",s)!= None:
        return len(re.split("\.",s)[1])
    else:
        return 0

def stringToNum(s):
    if isint(s):
        return int(s)

    elif isfloat(s):
        d = digit(s)
        return round(float(s),d)

    else:
        return None


def vround(number : float, digit : int = 3) -> float:
    m_obj = re.search('\.',str(number))
    if m_obj:
        zero_obj = re.search('^0\.0*',str(number))
        if zero_obj:
            return round(number,zero_obj.end() -2 + digit)
        else:
            if m_obj.start() >= digit:
                return int(number)
            else:
                return round(number, digit - m_obj.start())
    else:
        return int(number)