print('Loading i2c module...')

from modules.sensors.AtlasI2C import (
    AtlasI2C
)

from modules.sensors.SensorBase import SensorBase
from modules.app_config import socketio, cache

class i2cAPI(SensorBase):   

    def __init__(self):
        self.device_list = self.get_devices()
        self.active_i2c_devs = self.get_i2c_list(self.device_list)       
        for i in range(len(self.active_i2c_devs)):
            info = self.device_list[i].get_device_info().rstrip("\x00")
            b = info.split(" ")
            type = b[0]
            dev_name = super().sensor_type(type) # UPDATES S_COUNT TYPE TOTALS
            s_num = int(super().s_count['Total'] - 1)
            cache["INIT"].append({'l_type': 'passive', 'function': self.execute_I2C, 'sleep': 0.5, 'dev': self.device_list[i], 's_num': s_num})
            cache["SENSORS"][s_num] = {'com_type': "i2c", 'dev_name': dev_name, 'cur_read': "{0:.3f}".format(0)}      
   
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

    def execute_I2C(self, sleep, dev, s_num):
        print("Starting I2C Background Process on Sensor %s" % s_num)
        while True:
            try:                                 
                lines = dev.query("r")
                split_read = lines.split(":")
                read_raw = split_read[1].rstrip("\x00")
                new_read = float(read_raw)
            except: #except pylibftdi.FtdiError as e:         
                new_read = "ERR"
            super().Atlas_error_check(s_num, new_read)
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