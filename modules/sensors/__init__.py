import pprint

from modules.app_config import socketio, cache
from modules.sensors.i2c import *
from modules.sensors.ftdi import *

class SensorAPI:
    def __init__(self):
        cache["INIT"].append({"function": self.emit_reading, "sleep": 2})
        self.s_count = {'Total': 0, 'Temp': 0, 'pH': 0, 'SG': 0}
        self.prev_read = {}

    def log_error(self, msg):
        f_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        n_msg = '%s, %s' % (f_time, msg)
        print(n_msg)
        error_log = "./logs/TempError.log"
        with open(error_log, "a") as file:
            file.write("%s\n" % (n_msg))         
                        
    def emit_reading(self, sleep):
        print("Starting Emit Temp Thread")
        while True:
            f_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
            pprint.pprint(cache['SENSORS'])
            socketio.emit('cache', cache)
            socketio.sleep(sleep)

    def update_sensor_count(self, type):
        cur_s_count = self.s_count[type]
        self.s_count[type] = cur_s_count + 1
        cur_total = self.s_count['Total']
        self.s_count['Total'] = cur_total + 1
        self.prev_read[int(self.s_count['Total'] - 1)] = 0
        return self.s_count[type]
        
    def Atlas_error_check(self, s_num, new_read):
        try:
            if new_read == "ERR":
                msg = "Sensor Read Error @ Sensor %s" % (s_num)
                self.log_error(msg)
            else:   
                prev_read = self.prev_read[s_num]
                temp_dif = abs(new_read - prev_read) 
                if new_read <= 0 and prev_read <= 0:                        
                    set_val = "{0:.3f}".format(0)
                    cache['SENSORS'][s_num]['cur_read'] = set_val
                else:
                    if temp_dif < 20 or temp_dif == new_read:
                        set_val = "{0:.3f}".format(new_read)
                        cache['SENSORS'][s_num]['cur_read'] = set_val
                    else:                     
                        msg = "Large Value Change Error: sensor %s, Current Temp: %s, Previous Temp: %s" % (s_num, new_read, prev_read)
                        self.log_error(msg)
                self.prev_read[s_num] = new_read 
        except:
            msg = ("Error Running Temp Loop Thread on Sensor ", s_num)
            self.log_error(msg)           
        
