import time
from modules.app_config import *
from modules.sensors.AtlasI2C import (
    AtlasI2C
)


class tempAPI:   
    def __init__(self):
        self.temps = {'time': None, 0: 0, 1: 0, 2: 0}
        self.last_reading = [0,0,0]
        self.get_temp_indexes()
        self.device_list = self.get_devices()
        self.active_i2c_devs = self.get_i2c_list(self.device_list)
        thread1 = socketio.start_background_task(target=self.Atlas_Temp, dev_list=self.device_list, active_devs=self.active_i2c_devs, sleep=2)
   
    def get_devices(self):
        device = AtlasI2C()
        device_address_list = device.list_i2c_devices()
        device_list = []   
        for i in device_address_list:
            device.set_i2c_address(i)
            response = device.query("I")
            moduletype = response.split(",")[1] 
            response = device.query("name,?").split(",")[1]
            device_list.append(AtlasI2C(address = i, moduletype = moduletype, name = response))
        return device_list 

    def get_i2c_list(self, device_list):
        i2c_list = []
        for i in device_list:
                full = str(i.get_device_info())
                i2c_num2 = full.split(" ")
                i2c_num = int(i2c_num2[1])
                i2c_list.append(i2c_num)
        return i2c_list

    def get_reading(self, device_list,i2c_addr):
        try:
            for i in device_list:
                if(i.address == int(i2c_addr)):
                    device = i
                    switched = True
            if(switched):
                temp_raw = device.query("r")
                split_temp = temp_raw.split(":")
                temp = float(split_temp[1].rstrip("\x00"))            
        except:
            temp = "ERR"
        return temp

    def Atlas_Temp(self, dev_list, active_devs, sleep):
        print("Starting RTD Temp Background Process")
        while True:
            try:      
                # print("Last Temps: ", self.last_reading)  
                temp_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                self.temps['time'] = temp_time
                num_sensors = len(active_devs)
                for i in range(0, num_sensors):
                    i2c_addr = active_devs[i]                    
                    cur_temp = self.get_reading(dev_list,i2c_addr)
                    temp_dif = abs(cur_temp - self.last_reading[i]) 
                    if self.last_reading[i] == 0:
                        pass
                    else:
                        if cur_temp == "ERR":                        
                            msg = "%s, Error Running get_reading (float), temp_raw: %s" % (temp_time, cur_temp)
                            self.log_error(msg)
                        else:
                            if cur_temp <= 0:
                                pass
                            else:
                                if temp_dif < 20:
                                    self.temps[i] = cur_temp                      
                                else:
                                    msg = "%s, Temp Error: sensor %s, Current Temp: %s, Previous Temp: %s" % (temp_time, i, cur_temp, self.last_reading[i])
                                    self.log_error(msg)                    
                    self.last_reading[i] = cur_temp                                
                self.emit_temp()
            except:
                msg = "%s, Error Running Temp Loop Thread on Sensor %s" % (temp_time, i)
                self.log_error(msg)
            print("Temp Output: %s" % self.temps)
            socketio.sleep(sleep)

    def log_error(self, msg):
        error_log = "./logs/TempError.log"
        print(msg)
        with open(error_log, "a") as file:
            file.write("%s\n" % (msg))         
                        
    def emit_temp(self):
        socketio.emit('newtemps', self.temps)

    def get_temp_indexes(self):
        indexes = get_config_indexes()
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


#RUN FOR DEBUGGING PURPOSES                    
if __name__ == '__main__': 
    atest = tempAPI()
    device_list = atest.get_devices()
    active_i2c_devs = atest.get_i2c_list(device_list)
    print(active_i2c_devs)
    index = 1
    i2c_addr = active_i2c_devs[index]
    temp_reading = atest.get_reading(device_list,i2c_addr)
    print("t("+str(index)+")= %.3f" % (temp_reading))