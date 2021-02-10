#!/usr/bin/python

import io
import sys
import fcntl
import time
import copy
import string
from AtlasI2C import (
     AtlasI2C
)


def get_devices():
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

def get_i2c_list(device_list):
    i2c_list = []
    for i in device_list:
            full = str(i.get_device_info())
            i2c_num2 = full.split(" ")
            i2c_num = int(i2c_num2[1])
            i2c_list.append(i2c_num)
    return i2c_list

def get_reading(device_list,i2c_addr):
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


#RUN FOR DEBUGGING PURPOSES                    
if __name__ == '__main__': 
    device_list = get_devices()
    active_i2c_devs = get_i2c_list(device_list)
    print(active_i2c_devs)
    index = 1
    i2c_addr = active_i2c_devs[index]
    temp_reading = get_reading(device_list,i2c_addr)
    print("t("+str(index)+")= %.3f" % (temp_reading))