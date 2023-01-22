from modules.app_config import socketio, cache
from modules.sensors.i2c import *

class TempAPI:
    def __init__(self):
        cache["INIT"].append({"function": self.emit_temp, "sleep": 2})

    def log_error(self, msg):
        error_log = "./logs/TempError.log"
        print(msg)
        with open(error_log, "a") as file:
            file.write("%s\n" % (msg))         
                        
    def emit_temp(self, sleep):
        print("Starting Emit Temp Thread")
        while True:
            temp_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
            print(cache['SENSORS'])
            socketio.emit('newtemps', cache['SENSORS']) ###############   NEED TO FIX!!!!!!
            socketio.sleep(sleep)

    def get_temp_indexes(self, cache):
        indexes = cache['sensors']
        self.temp_indexes = indexes[0]

    def send_temp_indexes(self):
        socketio.emit('temp_indexes', self.temp_indexes)
        print("Sent Temp_indexes: ", self.temp_indexes)

    def temp_index_change(self, temp_indexes_in):
        self.temp_indexes = temp_indexes_in
        filename = "./config.txt"
        with open(filename, 'r') as f:
            cur_line = 0
            cfile = f.readlines()
            for line in cfile:
                cur_line +=1
                if "Temp_Indexes" in line:
                    cfile[cur_line] = str(self.temp_indexes) + '\n'
        with open(filename, 'w') as f:
            for i in range(0,len(cfile)):
                f.write(str(cfile[i]))
        socketio.emit('temp_indexes', self.temp_indexes)
        print("Temp_Indexes Received from Client & Broadcasted: %s" % self.temp_indexes)