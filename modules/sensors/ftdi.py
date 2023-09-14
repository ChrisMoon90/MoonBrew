print('Loading ftdi module...')

from pylibftdi.device import Device
from pylibftdi.driver import FtdiError
from pylibftdi import Driver
import time
import asyncio

from modules.sensors.SensorBase import SensorBase
from modules.app_config import socketio, cache

class ftdiAPI(SensorBase):
    
    def __init__(self, dev, type):
        self.dev = dev        
        self.dev_name = SensorBase.sensor_type(type)
        self.s_num = int(SensorBase.s_count['Total'] - 1)
        cache['INIT'].append({'function': self.execute_ftdi, 'sleep': 2})
        cache['SENSORS'][self.s_num] = {'com_type': 'ftdi', 'dev_name': self.dev_name, 'cur_read': "{0:.3f}".format(0)}     

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
            except: #except pylibftdi.FtdiError as e:         
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
        except FtdiError:
            print("Failed to read from the sensor.")
            return ''       

    def send_cmd(self, cmd):
        buf = cmd + "\r"
        try:
            self.write(buf)
            return True
        except FtdiError:
            print("Error: send_cmd failed.")
            return False


async def get_ftdi_device_list():
    dev_list = []    
    for device in Driver().list_devices():
        dev_info = device        
        vendor, product, serial = dev_info
        dev_list.append(serial)
    return dev_list

async def get_type(dev):
    dev.send_cmd('i')
    await socketio.sleep(1.5)
    info = dev.read_lines()
    b = info[0].split(',')
    type = b[1]
    return type

async def run():
    dev_list = await get_ftdi_device_list()
    for i in dev_list: 
        dev = Atlasftdi(i)
        type = await get_type(dev)
        d = ftdiAPI(dev, type)

loop = asyncio.get_event_loop()
# try:
loop.run_until_complete(run())
# except:
#     print('ftdi init error')
# finally:
#     loop.close()



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
        