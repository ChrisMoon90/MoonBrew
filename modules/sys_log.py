from datetime import datetime
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
        fmsg = str(datetime.now()) + ': ' + msg
        print(fmsg)
        with open(fn, "a") as f:
            f.write(fmsg + '\n')
    except Exception as e:
        print('sys_log error: ' + str(e))

