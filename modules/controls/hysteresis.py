print('Loading Hysteresis module...')

from modules.app_config import socketio, cache
from modules.controls.actors import ActorAPI
from modules.sys_log import sys_log

class HysteresisAPI(): 

    for k, v in cache['SYSTEM']['AutoStates'].items():
        vars()[k] = v  

    async def update_auto_states():
        for key, val in cache['SYSTEM']['AutoStates'].items(): 
            if val == True:
                if getattr(HysteresisAPI, key) == False:   
                    setattr(HysteresisAPI, key, val)                                 
                    thread = socketio.start_background_task(target=HysteresisAPI.hysteresis, vessel = key, sleep = 1)  
            else:
                if getattr(HysteresisAPI, key) == True: 
                    setattr(HysteresisAPI, key, val) 
                    a_indexes = await HysteresisAPI.get_a_indexes(cache['VESSELS'][key])
                    await HysteresisAPI.heat_chill_off(a_indexes)
        print('AutoStates Updated')

    async def heat_chill_off(a_indexes):
        for key, val in a_indexes.items():
            if key == "Heater" or key == "Chiller":
                if cache['ACTORS'][val]['state'] == True:
                    cache['ACTORS'][val]['state'] = False
        await ActorAPI.update_actors()

    async def get_a_indexes(v_dict):
        a_indexes = {}
        for key, val in v_dict['Actors'].items():
            if val['type'] == 'Heater':
                a_indexes['Heater'] = v_dict['Actors'][key]['index']
            elif val['type'] == 'Chiller':
                a_indexes['Chiller'] = v_dict['Actors'][key]['index']
        return a_indexes

    async def hysteresis(vessel, sleep):
        v_out = vessel.replace('_', ' ')
        a_msg = "Auto Control Started on " + v_out 
        sys_log(a_msg)      
        await socketio.emit('alert_success', a_msg)
        while getattr(HysteresisAPI, vessel): 
            update = False           
            v_dict = cache['VESSELS'][vessel]
            a_indexes = await HysteresisAPI.get_a_indexes(v_dict)
            cur_read = cache['SENSORS'][v_dict['Sensors'][0]['index']]['cur_read']
            tar_temp = v_dict['Params']['tar_temp']
            temp_tol = v_dict['Params']['temp_tol']
            try:
                if cur_read < 0:
                    cache['SYSTEM']['AutoStates'][vessel] = False
                    await HysteresisAPI.update_auto_states()
                else:
                    if 'Heater' in a_indexes:
                        if cur_read < tar_temp - temp_tol and cache['ACTORS'][a_indexes['Heater']]['state'] == False:
                            cache['ACTORS'][a_indexes['Heater']]['state'] = True
                            update = True
                        elif cur_read > tar_temp and cache['ACTORS'][a_indexes['Heater']]['state'] == True:
                            cache['ACTORS'][a_indexes['Heater']]['state'] = False
                            update = True
                    if 'Chiller' in a_indexes:
                        if cur_read > tar_temp + temp_tol and cache['ACTORS'][a_indexes['Chiller']]['state'] == False:
                            cache['ACTORS'][a_indexes['Chiller']]['state'] = True
                            update = True
                        elif cur_read < tar_temp and cache['ACTORS'][a_indexes['Chiller']]['state'] == True:
                            cache['ACTORS'][a_indexes['Chiller']]['state'] = False
                            update = True
                    if update == True:
                        await ActorAPI.update_actors()            
            except:
                print('Error running hysteresis loop on ' + vessel)
            await socketio.sleep(sleep)
        a_msg = "Auto Control Stopped on " + v_out
        sys_log(a_msg) 
        await socketio.emit('alert_warn', a_msg)