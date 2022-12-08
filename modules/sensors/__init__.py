import time
from modules.app_config import *
from modules.sensors.AtlasI2C import (
    AtlasI2C
)


class tempAPI:   
    def __init__(self):
        self.get_temp_indexes()
        self.device_list = self.get_devices()
        self.active_i2c_devs = self.get_i2c_list(self.device_list)       
        self.temps = {}
        self.last_reading = {}
        for i in range(len(self.active_i2c_devs)):
            thread = "sensor_thread_%s" % i
            self.temps[i] = "{0:.3f}".format(0)
            self.last_reading[i] = 0
            thread = socketio.start_background_task(target=self.Atlas_Temp, dev_list=self.device_list, i2c_addr=self.active_i2c_devs[i], i=i, sleep=0.5)
        socketio.sleep(1)
        emit_thread = socketio.start_background_task(target=self.emit_temp, sleep=2)
   
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

    def Atlas_Temp(self, dev_list, i2c_addr, i, sleep):
        print("Starting RTD Temp Background Process on I2C Dev %s" % i2c_addr)
        while True:
            try:      
                # print("Last Temps: ", self.last_reading) 
                temp_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())                    
                cur_temp = self.get_reading(dev_list, i2c_addr)
                temp_dif = abs(cur_temp - self.last_reading[i]) 
                if cur_temp == "ERR":
                    msg = "%s, Error Running get_reading (float), sensor %s, temp_raw: %s" % (temp_time, i2c_addr, cur_temp)
                    self.log_error(msg)
                else:
                    if cur_temp <= 0 and self.last_reading[i] <= 0:                        
                        self.temps[i] = "{0:.3f}".format(0)
                    else:
                        if temp_dif < 20 or temp_dif == cur_temp:
                            self.temps[i] = "{0:.3f}".format(cur_temp)                    
                        else:
                            msg = "%s, Large Temp Change Error: sensor %s, Current Temp: %s, Previous Temp: %s" % (temp_time, i2c_addr, cur_temp, self.last_reading[i])
                            self.log_error(msg)  
                self.last_reading[i] = cur_temp                                
            except:
                msg = "%s, Error Running Temp Loop Thread on Sensor %s" % (temp_time, i2c_addr)
                self.log_error(msg)           
            socketio.sleep(sleep)

    def log_error(self, msg):
        error_log = "./logs/TempError.log"
        print(msg)
        with open(error_log, "a") as file:
            file.write("%s\n" % (msg))         
                        
    def emit_temp(self, sleep):
        while True:
            temp_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
            print("Temp Output at %s --> %s" % (temp_time, self.temps))
            socketio.emit('newtemps', self.temps)
            socketio.sleep(sleep)

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