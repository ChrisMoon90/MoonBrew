import time
from modules.app_config import socketio, cache
from modules.sensors.AtlasI2C import (
    AtlasI2C
)

class i2cAPI:   
    def __init__(self, t):
        self.device_list = self.get_devices()
        dev_type = []
        for i in self.device_list:
            info = i.get_device_info().rstrip("\x00")
            b = info.split(" ")
            type = b[0]
            if type == "RTD":
                dev_type.append("Temp")
            elif type == "pH":
                dev_type.append("pH")
            else:
                dev_type.append("Other")
        # print("dev_types: %s" % dev_type)
        self.active_i2c_devs = self.get_i2c_list(self.device_list)       
        self.temps = {}
        self.last_reading = {}
        for i in range(len(self.active_i2c_devs)):
            thread = "sensor_thread_%s" % i
            self.temps[i] = "{0:.3f}".format(0)
            self.last_reading[i] = 0
            cache["INIT"].append({"function": self.Atlas_I2C_Temp, "sleep": 0.5, "sensor_num": i, "device": self.device_list[i], "dev_id": self.active_i2c_devs[i]})
            cache["SENSORS"][i] = {'type': dev_type[i], 'com_type': "i2c", 'dev_id': self.active_i2c_devs[i], 'prev_temp': self.last_reading[i], 'cur_temp': self.temps[i]}      
        socketio.sleep(1)
   
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

    def Atlas_I2C_Temp(self, sleep, sensor_num, device, dev_id):
        i2c_addr = dev_id
        i = sensor_num
        print("Starting RTD Temp Background Process on I2C Dev %s" % i2c_addr)
        while True:
            try:
                temp_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())                    
                temp_raw = device.query("r")
                split_temp = temp_raw.split(":")
                cur_temp = float(split_temp[1].rstrip("\x00"))
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
                cache["SENSORS"][i]['cur_temp'] = self.temps[i]
                cache["SENSORS"][i]['prev_temp'] = self.last_reading[i]
                self.last_reading[i] = cur_temp                                
            except:
                msg = "%s, Error Running Temp Loop Thread on Sensor %s" % (temp_time, i2c_addr)
                self.log_error(msg)           
            socketio.sleep(sleep)


#RUN FOR DEBUGGING PURPOSES                    
if __name__ == '__main__': 
    atest = i2cAPI()
    device_list = atest.get_devices()
    active_i2c_devs = atest.get_i2c_list(device_list)
    print(active_i2c_devs)
    index = 1
    i2c_addr = active_i2c_devs[index]
    temp_reading = atest.get_reading(device_list,i2c_addr)
    print("t("+str(index)+")= %.3f" % (temp_reading))