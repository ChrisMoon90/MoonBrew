print('Loading i2c module...')

import asyncio
from modules.sensors.AtlasI2C import (
    AtlasI2C
)

from modules.sensors.SensorBase import SensorBase
from modules.app_config import socketio, cache
from modules.sys_log import sys_log


class i2cAPI(SensorBase):   

    def __init__(self, dev):
        self.dev = dev 
        info = self.dev.get_device_info().rstrip("\x00")
        b = info.split(" ")
        type = b[0]
        self.dev_name = SensorBase.sensor_type(type)
        self.s_num = int(SensorBase.s_count['Total'] - 1)
        cache["INIT"].append({'function': self.execute_I2C, 'sleep': 2})
        cache["SENSORS"][self.s_num] = {'com_type': "i2c", 'dev_name': self.dev_name, 'cur_read': "{0:.3f}".format(0)}      

    async def execute_I2C(self, sleep):
        print("Starting I2C Thread on Sensor %s" % self.s_num)
        while True:
            try:                                 
                lines = await self.dev.query("r")
                split_read = lines.split(":")
                read_raw = split_read[1].rstrip("\x00")
                new_read = float(read_raw)
            except Exception as e: #except pylibftdi.FtdiError as e:         
                new_read = "ERR"
                sys_log('execute_I2C error: ', str(e))
            await SensorBase.Atlas_error_check(self.s_num, new_read)
            await socketio.sleep(sleep)


async def get_devices():
    device = AtlasI2C()
    device_address_list = device.list_i2c_devices()
    device_list = []   
    for i in device_address_list:
        device.set_i2c_address(i)
        response = await device.query("I")
        moduletype = response.split(",")[1] 
        resp = await device.query("name,?")
        response = resp.split(",")[1]
        device_list.append(AtlasI2C(address = i, moduletype = moduletype, name = response))
    return device_list 

async def i2c_init():
    device_list = await get_devices()
    for i in device_list:
        dev = i2cAPI(i)

loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(i2c_init())
except:
    print('i2c init error')


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