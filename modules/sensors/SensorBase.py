print('Loading SensorBase Module...')

import asyncio
import pprint
import time

from modules.app_config import socketio, cache
from modules.sys_log import sys_log

class SensorBase():

    s_count = {'Total': 0, 'Temp': 0, 'pH': 0, 'SG': 0}
    prev_read = {}    

    def sensor_type(type):
        if type == 'RTD':
            dev_name = 'Temp ' + str(SensorBase.update_sensor_count('Temp'))
        elif type == 'pH':
            dev_name = 'pH ' + str(SensorBase.update_sensor_count('pH'))
        else:
            dev_name = 'SG ' + str(SensorBase.update_sensor_count('SG'))
        return dev_name

    def update_sensor_count(type):
        cur_s_count = SensorBase.s_count[type]
        SensorBase.s_count[type] = cur_s_count + 1
        cur_total = SensorBase.s_count['Total']
        SensorBase.s_count['Total'] = cur_total + 1
        SensorBase.prev_read[int(SensorBase.s_count['Total'] - 1)] = 0
        return SensorBase.s_count[type]
                      
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

    async def Atlas_error_check(s_num, new_read):
        try:
            if new_read == "ERR":
                msg = "Sensor Read Error @ Sensor %s" % (s_num)
                sys_log(msg)
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
                        sys_log(msg)
                SensorBase.prev_read[s_num] = new_read 
        except Exception as e:
            sys_log('Error Running Temp Loop Thread on Sensor ' + str(s_num) + ': ' + str(e))      
        

cache['INIT'].append({'function': SensorBase.emit_reading, 'sleep': 5})