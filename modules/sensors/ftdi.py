print('Loading ftdi module...')

from pylibftdi.device import Device
from pylibftdi.driver import FtdiError
from pylibftdi import Driver
import time
import asyncio

from modules.sensors.SensorBase import SensorBase
from modules.app_config import socketio, cache
from modules.sys_log import sys_log


class ftdiAPI(SensorBase):
    
    def __init__(self, dev_id, type):
        self.dev_id = dev_id        
        self.dev_name = SensorBase.sensor_type(type)
        self.s_num = int(SensorBase.s_count['Total'] - 1)
        cache['INIT'].append({'function': self.execute_ftdi, 'sleep': 2})
        cache['SENSORS'][self.s_num] = {'dev_id': self.dev_id, 'com_type': 'ftdi', 'dev_name': self.dev_name, 'cur_read': "{0:.3f}".format(0)}     
    
    async def execute_ftdi(self, sleep):
        print("Starting FTDI Background Process on Sensor %s" % self.s_num)
        while True: 
            try:
                self.dev.send_cmd("R")
                await socketio.sleep(1.5)
                lines = self.dev.read_lines()
                for i in range(len(lines)):
                    if lines[i][0] != '*':
                        read_raw = lines[i]
                new_read = float(read_raw.strip())
            except Exception as e: #except pylibftdi.FtdiError as e:  
                sys_log('execute_ftdi error: ' + str(e))       
                new_read = "ERR"
            await SensorBase.Atlas_error_check(self.s_num, new_read)
            await socketio.sleep(sleep)


class Atlasftdi(Device):

    def __init__(self, dev):
        Device.__init__(self, mode='t', device_id=dev)

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
                    # self.flush_input()
                lines.append(line)
            return lines       
        except FtdiError as e:
            sys_log("FTDI read_lines error: " + str(e))
            return ''       

    def send_cmd(self, cmd):
        buf = cmd + "\r"
        try:
            self.write(buf)
            return True
        except FtdiError as e:
            sys_log("FTDI send_cmd error: " + str(e))
            return False


async def get_ftdi_device_list():
    dev_list = []    
    for device in Driver().list_devices():
        dev_info = device        
        vendor, product, serial = dev_info
        dev_list.append(serial)
    return dev_list

async def get_type(dev):
    try:
        dev.send_cmd('i')
        await socketio.sleep(1.5)
        info = dev.read_lines()
        print('ftdi dev info: ', str(info)) #Test
        b = info[0].split(',')
        type = b[1]
        return type
    except:
        print('FTDI comms error. Confirm chip is set to FTDI.')

async def run():
    dev_list = await get_ftdi_device_list()
    for i in dev_list: 
        dev = Atlasftdi(i)
        type = await get_type(dev)
        d = ftdiAPI(dev, type) #may change to dev to dev_id

async def re_init_ftdi():
    dev_list = await get_ftdi_device_list()
    for i in dev_list: 
        print(i)


loop = asyncio.get_event_loop()
loop.run_until_complete(run())


#RUN FOR DEBUGGING PURPOSES                    
if __name__ == '__main__': 
    f = ftdiAPI()
    dev_list = f.get_ftdi_device_list()
    dev_class_list = []
    for i in range(len(dev_list)):
        dev_class_list.append(Atlasftdi(dev_list[i]))
    while True:
        for i in range(len(dev_class_list)):
            try:
                dev_class_list[i].send_cmd("R")
                time.sleep(1.5)
                lines = dev_class_list[i].read_lines()
                for t in range(len(lines)):
                    print(lines)
                    if lines[t][0] != '*':
                        temp_raw = lines[t]
                temp = float(temp_raw.strip())
                print('temp: ', temp)
            except:
                print('ERROR')
            time.sleep(1)
        