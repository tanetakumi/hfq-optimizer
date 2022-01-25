import math
import re

def betac(calc_type: str, area: float = None, Rshunt: float= None, Rsubgap: float = 100, Cap : float = 0.064e-12, Ic: float = 0.1e-3, betac: float = 1) -> float:
    phi = 2.068 * 10 ** -15
    

    if re.fullmatch('area', calc_type, flags= re.IGNORECASE):
        if Rshunt == None:
            raise ValueError('areaを計算するときはRshuntの値を入力してください。')
        
        denomi = Rshunt * ( math.sqrt(2 * math.pi * Ic * Cap / (phi * betac)) - 1/Rsubgap )
        return 1/denomi

    elif re.fullmatch('betac', calc_type, flags= re.IGNORECASE):
        if area == None or Rshunt == None:
            raise ValueError('betacを計算するときはarea, Rshuntの値を入力してください。')

        _Cap = Cap * area
        _Ic = Ic * area
        _Rsubgap = Rsubgap / area
        Rj = Rshunt * _Rsubgap/(Rshunt + _Rsubgap)

        return (2 * math.pi * _Ic * _Cap * Rj**2) / phi

    elif re.fullmatch('shunt', calc_type, flags= re.IGNORECASE):
        if area == None:
            raise ValueError('Rshuntを計算するときはareaの値を入力してください。')
        _Cap = Cap * area
        _Ic = Ic * area
        _Rsubgap = Rsubgap / area
        denomi = math.sqrt(2 * math.pi * _Ic * _Cap / (phi * betac)) - 1/_Rsubgap
        return 1/denomi

    else:
        raise ValueError('calc_type(計算タイプ)の値が読み取れません。')

if __name__ == "__main__":
    print(betac(calc_type='shunt', area=0.5))

