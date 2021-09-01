import time
from modules.app_config import *
from modules.sensors.AtlasI2C import (
    AtlasI2C
)


class tempAPI:   
    def __init__(self):
        self.temps = {'time': None, 0: None, 1: None, 2: None}
   
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
                long_temp = device.query("r")
                split_temp = long_temp.split(":")
                temp = float(split_temp[1].rstrip("\x00"))            
                return temp
        except IOError:
            print("Query failed \n - Address may be invalid, use list command to see available addresses")

    def RTD_Temp(self, dev_list, active_devs, sleep):
        print("Starting RTD Temp Background Process")
        while True:        
            temp_time = time.strftime("%H:%M:%S", time.localtime())
            self.temps['time'] = temp_time
            num_sensors = len(active_devs)
            for i in range(0, num_sensors):
                i2c_addr = active_devs[i]
                cur_temp = self.get_reading(dev_list,i2c_addr)           
                self.temps[i] = cur_temp
            print("Temp Output: %s" % self.temps)      
            self.emit_temp()
            socketio.sleep(sleep)
                        
    def emit_temp(self):
        socketio.emit('newtemps', self.temps)


class logAPI:
    def __init__(self, a):
        self.running = False
        self.temps = a.temps

    def set_run_state(self, logState):
        self.running = logState
        print("Logging run_state changed: ", self.running)

    def save_to_file(self, sleep):
        print("Starting Logging")
        while self.running:
            filename = "./logs/Temps.log"
            formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            msg = "%s, %s\n" % (formatted_time, self.temps)
            print("Saving to File: %s" %self.temps)
            with open(filename, "a") as file:
                file.write(msg)
            socketio.sleep(sleep)
        print("Log Thread Terminated")



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