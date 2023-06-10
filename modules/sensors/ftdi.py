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
        dev = Atlasftdi(t, dev)
        dev.send_cmd('i')
        socketio.sleep(1.5)
        info = dev.read_lines()
        # print(info)
        b = info[0].split(',')
        type = b[1]
        # print(type)
        if type == 'RTD':
            dev_id = 'Temp ' + str(t.update_sensor_count('Temp'))
        else:
            dev_id = 'pH ' + str(t.update_sensor_count('pH'))
        s_num = int(t.s_count['Total'] - 1)
        cache['INIT'].append({'function': execute_ftdi, 'sleep': 0.5, 'dev': dev, 's_num': s_num})
        cache['SENSORS'][s_num] = {'com_type': 'ftdi', 'dev_id': dev_id, 'prev_read': last_reading, 'cur_read': temp}      
    # socketio.sleep(1)

# class ftdiAPI:
def execute_ftdi(sleep, dev, s_num):
    print('Made it to ftdi execute!')
    while True:
        f_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        prev_read = cache['SENSORS'][s_num]['cur_read']
        try:
            dev.send_cmd("R")
            socketio.sleep(1.5)
            lines = dev.read_lines()
            for i in range(len(lines)):
                if lines[i][0] != '*':
                    temp_raw = lines[i]
        except: #except pylibftdi.FtdiError as e:         
            msg = "%s, Error running send_cmd @ sensor %s\n" % (f_time, s_num)
            log_error("%s\n" % (msg))
            temp_raw = "ERR"
            socketio.sleep(sleep)
        try:
            if temp_raw == "ERR":
                pass
            else:
                new_read = float(temp_raw.strip())
                # cur_temp = float(split_temp[1].rstrip("\x00"))
                temp_dif = abs(new_read - prev_read) 
                if new_read <= 0 and prev_read <= 0:                        
                    set_val = "{0:.3f}".format(0)
                else:
                    if temp_dif < 20 or temp_dif == new_read:
                        set_val = "{0:.3f}".format(new_read)                    
                    else:
                        msg = "%s, Large Value Change Error: sensor %s, Current Temp: %s, Previous Temp: %s" % (f_time, s_num, new_read, prev_read)
                        log_error(msg) 
                        set_val = prev_read
                cache["SENSORS"][s_num]['cur_read'] = set_val
            #     cache["SENSORS"][s_num]['prev_read'] = prev_read
            # self.last_reading[i] = cur_temp                             
        except:
            msg = "%s, Error Running Temp Loop Thread on Sensor %s" % (f_time, s_num)
            log_error(msg)           
        socketio.sleep(sleep)

def log_error(msg):
    print(msg)
    error_log = "./logs/TempError.log"
    with open(error_log, "a") as file:
        file.write(msg)

def get_ftdi_device_list():
    dev_list = []    
    for device in Driver().list_devices():
        dev_info = device        
        vendor, product, serial = dev_info   # device must always be this triple
        # print(dev_info)
        dev_list.append(serial)
    # print('ftdi dev_list: ', str(dev_list))
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
        