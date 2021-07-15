import time
#from datetime import datetime, timedelta

#from modules import socketio
from modules.app_config import *
import modules.sensors.AtlasI2C as AtlasI2C
import modules.sensors.sensor_i2c as sensor_i2c

device_list = sensor_i2c.get_devices()
active_i2c_devs = sensor_i2c.get_i2c_list(device_list)
print("Active I2C Devices: %s" % active_i2c_devs)

temps = {'time': None, 0: None, 1: None, 2: None}
def RTD_Temp(sleep):
    print("Starting RTD Temp Background Process")
    global temps
    while True:        
        temp_time = time.strftime("%H:%M:%S", time.localtime())
        temps['time'] = temp_time
        num_sensors = len(active_i2c_devs)
        for i in range(0, num_sensors):
            i2c_addr = active_i2c_devs[i]
            cur_temp = sensor_i2c.get_reading(device_list,i2c_addr)           
            temps[i] = cur_temp
        print("Temp Output: %s" % temps)      
        emit_temp(temps)
        socketio.sleep(sleep)
                     
def emit_temp(temps):
    socketio.emit('newtemps', temps)

def save_to_file(sleep):
    print("Starting save_to_file")
    socketio.sleep(5)
    while True:
        filename = "./logs/Temps.log"
        formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        msg = "%s, %s\n" % (formatted_time, temps)
        print("Saving to File: %s" %temps)
        with open(filename, "a") as file:
            file.write(msg)
        socketio.sleep(sleep)
