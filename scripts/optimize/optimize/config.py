

def check_config(config):
    if "phase.ele" or "voltage.ele" in config:
        print(config["start.time"])
    else:
        print("testst")
