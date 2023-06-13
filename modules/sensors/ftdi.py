from pylibftdi.device import Device
from pylibftdi.driver import FtdiError
from pylibftdi import Driver
import time

from modules.app_config import socketio, cache

def init_ftdi(t):
    dev_list = get_ftdi_device_list()
    for i in range(len(dev_list)):  
        dev = dev_list[i]
        dev = Atlasftdi(t, dev)
        dev.send_cmd('i')
        socketio.sleep(1.5)
        info = dev.read_lines()
        b = info[0].split(',')
        type = b[1]
        if type == 'RTD':
            dev_id = 'Temp ' + str(t.update_sensor_count('Temp'))
        else:
            dev_id = 'pH ' + str(t.update_sensor_count('pH'))
        s_num = int(t.s_count['Total'] - 1)
        cache['INIT'].append({'function': execute_ftdi, 't': t, 'sleep': 0.5, 'dev': dev, 's_num': s_num})
        cache['SENSORS'][s_num] = {'com_type': 'ftdi', 'dev_id': dev_id, 'cur_read': "{0:.3f}".format(0)}      

# class ftdiAPI:
def execute_ftdi(t, sleep, dev, s_num):
    print("Starting FTDI Background Process on Sensor %s" % s_num)
    while True: 
        try:
            dev.send_cmd("R")
            socketio.sleep(1.5)
            lines = dev.read_lines()
            for i in range(len(lines)):
                if lines[i][0] != '*':
                    read_raw = lines[i]
            new_read = float(read_raw.strip())
        except: #except pylibftdi.FtdiError as e:         
            new_read = "ERR"
        t.Atlas_error_check(s_num, new_read)
        socketio.sleep(sleep)

def get_ftdi_device_list():
    dev_list = []    
    for device in Driver().list_devices():
        dev_info = device        
        vendor, product, serial = dev_info   # device must always be this triple
        dev_list.append(serial)
    return dev_list


class Atlasftdi(Device):
    def __init__(self, t, dev):
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
        buf = cmd + "\r"        # add carriage return
        try:
            self.write(buf)
            return True
        except FtdiError:
            print("Error: send_cmd failed.")
            return False


#RUN FOR DEBUGGING PURPOSES                    
if __name__ == '__main__': 
    dev_list = get_ftdi_device_list()
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
        