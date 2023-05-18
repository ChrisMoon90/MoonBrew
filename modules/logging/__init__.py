import time
import os
from modules.app_config import socketio, cache


class logAPI:
    def __init__(self, a):
        self.running = False
        self.log_rate = cache['SYSTEM']['Static']['log_rate']
        self.filename = "./logs/Temps.csv"

    def set_log_rate(self):
        self.log_rate = cache['SYSTEM']['Static']['log_rate']

    def set_log_state(self):
        self.running = cache['SYSTEM']['Dynamic']['log_state']
        print('log_state', self.running)
        if self.running:
            t = socketio.start_background_task(target=self.save_to_file)
        else:
            print("Stopping Logging Thread") 

    def save_to_file(self):
        print("Starting Logging")
        while self.running: 
            log_rate = eval(self.log_rate) * 60
            ft = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            r = []
            for i in cache['SENSORS']:
                r.append(cache['SENSORS'][i]['cur_read'])
            msg = "%s, %.3f, %.3f, %.3f" % (ft, eval(r[0]), eval(r[1]), eval(r[2]))
            print("Saving to File: %s" % msg)
            if os.path.exists(self.filename):
                with open(self.filename, "a") as f:
                    f.write("%s\n" % msg)
            else:
                print("Temp.csv file does not exist. File will be created.")
                header = "Time, Sensor 1, Sensor 2, Sensor 3\n"
                with open(self.filename, 'a') as f:
                    f.write(header)
                    f.write("%s\n" % msg)
            socketio.sleep(log_rate)
        print("Log Thread Terminated")

    def delete_log(self):   
        if os.path.exists(self.filename):
            os.remove(self.filename)
            msg = "Temp Log File Successfully Deleted"
            print(msg)
            socketio.emit('log_deleted', msg)
        else:
            print("The file does not exist")