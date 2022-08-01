from .util import isfloat, isint

class Config:
    def __init__(self, config_data : dict):
        # 全て確認
        for k in ["avgcalc.start.time", "avgcalc.end.time", "pulse.delay", "pulse.interval","phase.ele","voltage.ele","allow.multi.swithes"]:
            if not k in config_data:
                raise ValueError("\033[31m["+k+"]の値が読み取れません。"+"\033[0m")
        
        self.start_time = config_data["avgcalc.start.time"] if isfloat(config_data["avgcalc.start.time"]) else exec('raise ValueError("\033[31m["avgcalc.start.time"]の値が読み取れません。"+"\033[0m")')

        self.end_time = config_data["avgcalc.end.time"] if isfloat(config_data["avgcalc.end.time"]) else exec('raise ValueError("\033[31m["avgcalc.end.time"]の値が読み取れません。"+"\033[0m")')
