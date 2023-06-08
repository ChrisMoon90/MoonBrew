from pylibftdi.device import Device
from pylibftdi.driver import FtdiError
from pylibftdi import Driver
import time

from modules.app_config import socketio, cache

def init_ftdi(t):
    dev_list = get_ftdi_device_list()
    for i in range(len(dev_list)):
        temp = "{0:.3f}".format(0)
        last_reading = 0    
        dev = dev_list[i]
        dev_class = ftdiAPI(t, dev)
        dev_class.send_cmd('i')
        socketio.sleep(1.5)
        info = dev_class.read_lines()
        print(info)
        b = info[0].split(',')
        type = b[1]
        print(type)
        if type == 'RTD':
            dev_id = 'Temp ' + str(t.update_sensor_count('Temp'))
        elif type == 'pH':
            dev_id = 'pH ' + str(t.update_sensor_count('pH'))
        else:
            dev_id = 'SG ' + str(t.update_sensor_count('SG'))
        sensor_num = t.s_count['Total']
        cache['INIT'].append({'com_type': 'ftdi', 'function': execute_ftdi, 'sleep': 0.5, 'sensor_num': sensor_num, 'device': dev, 'dev_id': dev_class})
        cache['SENSORS'][sensor_num] = {'com_type': 'ftdi', 'dev_id': dev_id, 'prev_read': last_reading, 'cur_read': temp}      
    socketio.sleep(1)

def execute_ftdi(self):
    print('Made it to ftdi execute!')
    # self.index = self.sensorSelect
    # self.devices = get_ftdi_device_list()
    # self.dev = AtlasDevice(self.devices[int(self.index)])
    # while self.is_running():
    #     try:
    #         self.dev.send_cmd("R")
    #         self.sleep(1.5) #MADE THIS SOCKETIOSLEEP & FIXED LATENCY ISSUE
    #         lines = self.dev.read_lines()
    #         for i in range(len(lines)):
    #             if lines[i][0] != '*':
    #                 temp_raw = lines[i]
    #     except: #except pylibftdi.FtdiError as e:
    #         formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    #         msg = "%s, Error running get_temp @ dev: %s\n" % (formatted_time, self.dev)
    #         print(msg)
    #         log_error("%s\n" % (msg))
    #         temp_raw = "ERR"
    #         self.sleep(1.5)
    #     try:
    #         new_reading = float(temp_raw.strip())
    #         temp_dif = abs(new_reading - self.last_reading)
    #         if temp_dif > 10:                 
    #             formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    #             msg = "%s, New Reading: %s, Old Reading: %s, dev_index: %s" % (formatted_time, new_reading, self.last_reading, self.index)
    #             print(msg)
    #             log_error("%s\n" % (msg))                  
    #         else:
    #             self.data_received(new_reading)
    #             send_to_logging(self.index, new_reading)
    #             print("Sensor Reading from index %s = %s" % (self.index, new_reading))
    #         self.last_reading = new_reading
    #     except:
    #         formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    #         msg = "%s, Error converting temp_raw to float: %s, dev_index: %s" % (formatted_time, temp_raw, self.index)
    #         print(msg)
    #         log_error("%s\n" % (msg))
    #     self.sleep(2)

def get_ftdi_device_list():
    dev_list = []    
    for device in Driver().list_devices():
        dev_info = device        
        vendor, product, serial = dev_info   # device must always be this triple
        print(dev_info)
        dev_list.append(serial)
    print('ftdi dev_list: ', str(dev_list))
    return dev_list

def log_error(self, msg):
    error_log = "./logs/TempError.log"
    with open(error_log, "a") as file:
        file.write(msg)


class ftdiAPI(Device):
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
                    self.flush_input()
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
        dev_class_list.append(ftdiAPI(dev_list[i]))
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
        