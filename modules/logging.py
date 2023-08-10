print('Loading Logging module...')

import time
import os
from modules.app_config import socketio, cache
from modules.cache import CacheAPI


class logAPI:
    run_state = False
    log_rate = cache['SYSTEM']['Static']['log_rate']
    filename = "./logs/Temps.csv"

    # def __init__(self):
    #     self.running = False
    #     self.log_rate = cache['SYSTEM']['Static']['log_rate']
    #     self.filename = "./logs/Temps.csv"

    def set_log_rate(self):
        logAPI.log_rate = cache['SYSTEM']['Static']['log_rate']

    def set_log_state(self):
        logAPI.run_state = cache['SYSTEM']['Dynamic']['log_state']
        print('log_state', logAPI.run_state)
        if logAPI.run_state:
            t = socketio.start_background_task(target = logAPI.save_to_file)
        else:
            print("Stopping Logging Thread") 

    def save_to_file(self):
        print("Starting Logging...")
        a_msg = 'Logging Started'
        socketio.emit('alert_success', a_msg)
        while logAPI.run_state: 
            self.set_log_rate()
            print('log rate: ', logAPI.log_rate)
            log_rate = eval(logAPI.log_rate) * 60
            ft = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            r = []
            for i in cache['SENSORS']:
                r.append(cache['SENSORS'][i]['cur_read'])
            msg = ft
            for x in r:
                val = "%.3f" % eval(x)
                msg += ', ' + val
            print("Saving to File: %s" % msg)
            if os.path.exists(logAPI.filename):
                with open(logAPI.filename, "a") as f:
                    f.write("%s\n" % msg)
            else:
                print("Temp.csv file does not exist. File will be created.")
                header = "Time, Sensor 1, Sensor 2, Sensor 3\n"
                with open(logAPI.filename, 'a') as f:
                    f.write(header)
                    f.write("%s\n" % msg)
            socketio.sleep(log_rate)
        a_msg = 'Logging Stopped'
        print(a_msg)
        socketio.emit('alert_warn', a_msg)

    def delete_log(self):   
        if os.path.exists(logAPI.filename):
            os.remove(logAPI.filename)
            a_msg = "Log File Successfully Deleted"
            print(a_msg)
            socketio.emit('alert_success', a_msg)
        else:
            a_msg = "Log File not Deleted: file does not exist"
            print(a_msg)
            socketio.emit('alert_warn', a_msg)


# LOG SOCKETIO FUNCTIONS ############################
@socketio.on('set_log_state')
def set_log_state(s_dict):
    CacheAPI.update_cache('SYSTEM', s_dict)
    logAPI.set_log_state()

@socketio.on('delete_log')
def del_log():
    logAPI.delete_log()