import string
import pylibftdi
from pylibftdi.device import Device
from pylibftdi.driver import FtdiError
from pylibftdi import Driver
import os
import time


class AtlasDevice(Device):

    def __init__(self, sn):
        Device.__init__(self, mode='t', device_id=sn)

    def read_line(self, size=0):
        lsl = len('\r')
        line_buffer = []
        while True:
            next_char = self.read(1)
            if next_char == '' or (size > 0 and len(line_buffer) > size):
                break
            line_buffer.append(next_char)
            if (len(line_buffer) >= lsl and
                    line_buffer[-lsl:] == list('\r')):
                break
        return ''.join(line_buffer)
    
    def read_lines(self):
        lines = []
        try:
            while True:
                line = self.read_line()
                if not line:
                    break
                    self.flush_input()
                lines.append(line)
            #print(lines)
            return lines       
        except FtdiError:
            print("Failed to read from the sensor.")
            return ''       

    def send_cmd(self, cmd):
        buf = cmd + "\r"        # add carriage return
        #print("buf = ", buf)
        try:
            self.write(buf)
            #print("SND =", self.write(buf))
            return True
        except FtdiError:
            print("Failed to send command to the sensor.")
            return False


def get_ftdi_device_list():
    dev_list = []    
    for device in Driver().list_devices():
        dev_info = device        
        vendor, product, serial = dev_info   # device must always be this triple
        dev_list.append(serial)
    return dev_list

def get_sensor(index):  #SELECT DEVICE   
    print("Index2 = ", index)
    devices = get_ftdi_device_list()
    while True:
        try:
            dev = AtlasDevice(devices[int(index)])
            return dev
        except pylibftdi.FtdiError as e:
            print( "Error0, ", e)
            time.sleep(2)

def get_temp(dev_IN):    #COLLECT TEMP READING
    dev_IN.send_cmd("C,0") # turn off continuous mode
    dev_IN.flush()
    while True:
        try:
            dev_IN.send_cmd("R")
            lines = dev_IN.read_lines()
            for i in range(len(lines)):
                if lines[i][0] != '*':
                    temp = lines[i]
                    return temp
        except pylibftdi.FtdiError as e:
                print( "Error1, ", e)
                time.sleep(2)

def run_Temp(dev_active):
    print("dev_active = ", dev_active)
    dev_active.send_cmd("C,0") # turn off continuous mode
    dev_active.flush()
    try:
        while True:
            temp_long = get_temp(dev_active)
            temp = round(float(temp_long), 2)
            #print("Response: = ",temp)
            return temp
    except pylibftdi.FtdiError as e:
        print("Error1, ", e)
        time.sleep(2)


#USE BELOW FOR DEBUGGING
if __name__ == '__main__':
    index = 0
    dev_active = get_sensor(index)
    q = run_Temp(dev_active)
    print("q = ", q)
    
    dlist = get_ftdi_device_list()
    print(">> Opened device ", dlist[0])
    delaytime = 2
    dev_active.send_cmd("C,0") # turn off continuous mode
    dev_active.flush()
    try:
        while True:  #WHILE LOOP RUNS CONTINUOUSLY UNTIL INTERRUPT
            ttemp = get_temp(dev_active)
            print("Response: = ",ttemp)
            time.sleep(delaytime)
    
    except KeyboardInterrupt: # catches the ctrl-c command, which breaks the loop above
        print("Continuous Polling Stopped")
    
        
    #real_raw_input = vars(__builtins__).get('raw_input', input) # used to find the correct function for python2/3      
    #@blueprint.route('/<int:t>', methods=['GET'])
    #def set_temp(t):
    #print("Polling sensor every %0.2f seconds, press ctrl-c to stop polling" % delaytime)

    