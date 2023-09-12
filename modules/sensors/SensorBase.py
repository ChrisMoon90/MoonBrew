print('Loading SensorBase Module...')

import asyncio
import pprint
import time

from modules.app_config import socketio, cache

class SensorBase():
    s_count = {'Total': 0, 'Temp': 0, 'pH': 0, 'SG': 0}
    prev_read = {}    
                        
    async def emit_reading(sleep):
        print("Starting Emit Reading Thread")
        await socketio.sleep(3)
        while True:
            f_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
            print(70 * "-")
            print(f_time)
            pprint.pprint(cache['SENSORS'])
            await socketio.emit('cache', cache)
            await socketio.sleep(sleep)

    def update_sensor_count(self, type):
        cur_s_count = SensorBase.s_count[type]
        SensorBase.s_count[type] = cur_s_count + 1
        cur_total = SensorBase.s_count['Total']
        SensorBase.s_count['Total'] = cur_total + 1
        SensorBase.prev_read[int(SensorBase.s_count['Total'] - 1)] = 0
        return SensorBase.s_count[type]
        
    def Atlas_error_check(self, s_num, new_read):
        try:
            if new_read == "ERR":
                msg = "Sensor Read Error @ Sensor %s" % (s_num)
                self.log_error(msg)
            else:   
                prev_read = SensorBase.prev_read[s_num]
                temp_dif = abs(new_read - prev_read) 
                # set_val = "{0:.3f}".format(0)
                if new_read <= 0 and prev_read <= 0:                        
                    cache['SENSORS'][s_num]['cur_read'] = new_read
                else:
                    if temp_dif < 20 or temp_dif == new_read:
                        cache['SENSORS'][s_num]['cur_read'] = new_read
                    else:                     
                        msg = "Large Value Change Error: sensor %s, Current Temp: %s, Previous Temp: %s" % (s_num, new_read, prev_read)
                        SensorBase.log_error(SensorBase, msg)
                SensorBase.prev_read[s_num] = new_read 
        except:
            msg = ("Error Running Temp Loop Thread on Sensor ", s_num)
            SensorBase.log_error(msg)           
        
    def sensor_type(self, type):
        if type == 'RTD':
            dev_name = 'Temp ' + str(SensorBase.update_sensor_count(SensorBase, 'Temp'))
        elif type == 'pH':
            dev_name = 'pH ' + str(SensorBase.update_sensor_count(SensorBase, 'pH'))
        else:
            dev_name = 'SG ' + str(SensorBase.update_sensor_count(SensorBase, 'SG'))
        return dev_name
        
    def log_error(self, msg):
        f_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        n_msg = '%s, %s' % (f_time, msg)
        print(n_msg)
        error_log = "./logs/TempError.log"
        with open(error_log, "a") as file:
            file.write("%s\n" % (n_msg)) 


cache['INIT'].append({'function': SensorBase.emit_reading, 'sleep': 5})