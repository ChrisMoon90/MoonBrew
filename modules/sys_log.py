import time
import os

def sys_log(msg):
    fn = './logs/system.txt'
    try:
        if os.path.exists(fn):
            pass
        else:
            print("System Log file does not exist. One will be created.")
            with open(fn, 'w') as f:
                f.write("SYSTEM LOG\n")
        c_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        with open(fn, "a") as f:
            f.write(str(c_time) + ': ' + msg + '\n')
    except Exception as e:
        print('MBC_log error: ' + str(e))

