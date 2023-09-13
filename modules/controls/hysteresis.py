print('Loading Hysteresis module...')

from modules.app_config import socketio, cache
from modules.controls.actors import ActorAPI

class HysteresisAPI(): 

    for k, v in cache['SYSTEM']['AutoStates'].items():
        vars()[k] = v

    # def __init__(self):
    #     for key, val in cache['SYSTEM']['AutoStates'].items():
    #         setattr(HysteresisAPI, key, val)     

    async def update_auto_states():
        for key, val in cache['SYSTEM']['AutoStates'].items(): 
            if val == True:
                if getattr(HysteresisAPI, key) == False:   
                    setattr(HysteresisAPI, key, val)                                 
                    thread = socketio.start_background_task(target=HysteresisAPI.hysteresis, vessel = key, sleep = 2)                  
            setattr(HysteresisAPI, key, val) 
        print('AutoStates Updated')
        # await socketio.emit('cache', cache)

    async def heat_chill_off(a_indexes):
        for key, val in a_indexes.items():
            if key == "Heater" or key == "Chiller":
                if cache['ACTORS'][val]['state'] == True:
                    cache['ACTORS'][val]['state'] = False
        await ActorAPI.update_actors()

    async def hysteresis(vessel, sleep):
        a_msg = "Auto Control Started on " + vessel       
        print(a_msg)
        await socketio.emit('alert_success', a_msg)
        while getattr(HysteresisAPI, vessel):
            a_indexes = {}
            v_dict = cache['VESSELS'][vessel]
            for key, val in v_dict['Actors'].items():
                if val['type'] == 'Heater':
                    a_indexes['Heater'] = v_dict['Actors'][key]['index']
                elif val['type'] == 'Chiller':
                    a_indexes['Chiller'] = v_dict['Actors'][key]['index']
            cur_read = cache['SENSORS'][v_dict['Sensors'][0]['index']]['cur_read']
            tar_temp = v_dict['Params']['tar_temp']
            temp_tol = v_dict['Params']['temp_tol']
            try:
                if 'Heater' in a_indexes:
                    if cur_read < tar_temp - temp_tol and cache['ACTORS'][a_indexes['Heater']]['state'] == False:
                        cache['ACTORS'][a_indexes['Heater']]['state'] = True
                    elif cur_read > tar_temp and cache['ACTORS'][a_indexes['Heater']]['state'] == True:
                        cache['ACTORS'][a_indexes['Heater']]['state'] = False
                if 'Chiller' in a_indexes:
                    if cur_read > tar_temp + temp_tol and cache['ACTORS'][a_indexes['Chiller']]['state'] == False:
                        cache['ACTORS'][a_indexes['Chiller']]['state'] = True
                    elif cur_read < tar_temp and cache['ACTORS'][a_indexes['Chiller']]['state'] == True:
                        cache['ACTORS'][a_indexes['Chiller']]['state'] = False
                await ActorAPI.update_actors()            
            except:
                print('Error running hysteresis loop on ' + vessel)
            await socketio.sleep(sleep)
        await HysteresisAPI.heat_chill_off(a_indexes)
        a_msg = "Auto Control Terminated on " + vessel
        print(a_msg)
        await socketio.emit('alert_warn', a_msg)