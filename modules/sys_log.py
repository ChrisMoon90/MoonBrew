from datetime import datetime
import os

def sys_log(msg):
    dir = './logs/'
    fn = 'system.txt'
    try:
        if os.path.exists(dir + fn):
            pass
        else:
            print("System Log file does not exist. One will be created.")
            if os.path.isdir(dir):
                pass
            else:
                os.mkdir(dir)
            with open(dir + fn, 'w') as f:
                f.write("SYSTEM LOG\n")
        fmsg = str(datetime.now()) + ': ' + str(msg)
        print(fmsg)
        with open(dir + fn, "a") as f:
            f.write(fmsg + '\n')
    except Exception as e:
        print('sys_log error: ' + str(e))

