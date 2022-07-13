
def check_config(config_data) -> bool:

    for k in ["avgcalc.start.time", "avgcalc.end.time", "pulse.delay", "pulse.interval"]:
        if k in config_data:
            if not type(config_data[k])==float:
                raise ValueError("\033[31m["+k+"]の値が読み取れません。"+"\033[0m")
        else:
            raise ValueError("\033[31m["+k+"]の値が読み取れません。"+"\033[0m")

    for k in ["phase.ele", "voltage.ele"]:
        if k in config_data:
            if not config_data[k] == []:
                if not type(config_data[k][0])==list:
                    raise ValueError("\033[31m["+k+"]の値が読み取れません。"+"\033[0m")
        else:
            raise ValueError("\033[31m["+k+"]の値が読み取れません。"+"\033[0m")

    for k in ["allow.multi.swithes"]:
        if k in config_data:
            if not type(config_data[k])==bool:
                raise ValueError("\033[31m["+k+"]の値が読み取れません。"+"\033[0m")
        else:
            raise ValueError("\033[31m["+k+"]の値が読み取れません。"+"\033[0m")
    
    return True