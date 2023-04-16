from modules.app_config import socketio, cache
from modules.sensors.i2c import *

class SensorAPI:
    def __init__(self):
        cache["INIT"].append({"function": self.emit_reading, "sleep": 2})
        self.s_count = {'Temp': 0, 'pH': 0, 'SG': 0}

    def log_error(self, msg):
        error_log = "./logs/TempError.log"
        print(msg)
        with open(error_log, "a") as file:
            file.write("%s\n" % (msg))         
                        
    def emit_reading(self, sleep):
        print("Starting Emit Temp Thread")
        while True:
            temp_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
            print(cache['SENSORS'])
            socketio.emit('cache', cache)
            socketio.sleep(sleep)

    def update_sensor_count(self, type):
        cur_s_count = self.s_count[type]
        self.s_count[type] = cur_s_count + 1
        return self.s_count[type]