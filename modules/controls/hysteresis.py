from pprint import pprint

from modules.actors.__init__ import ActorAPI
from modules.app_config import socketio, cache


class HysteresisAPI(ActorAPI):

    def __init__(self):
        for key, val in cache['SYSTEM']['AutoStates'].items():
            setattr(HysteresisAPI, key, val)
        # pprint(vars(self))

    def update_auto_states(self):
        for key, val in cache['SYSTEM']['AutoStates'].items(): 
            if val == True:
                if getattr(HysteresisAPI, key) == False:   
                    setattr(HysteresisAPI, key, val)                                 
                    thread = socketio.start_background_task(target=self.hysteresis, vessel = key, sleep = 2)                  
            setattr(HysteresisAPI, key, val) 

    def hysteresis(self, vessel, sleep):
        a_msg = "Auto Control Started on " + vessel
        print(a_msg)
        socketio.emit('alert_success', a_msg)
        v_dict = cache['VESSELS'][vessel]
        while getattr(HysteresisAPI, vessel):
            a_indexes = {}
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
                        print('heat on', a_indexes['Heater'])
                        cache['ACTORS'][a_indexes['Heater']]['state'] = True
                    elif cur_read > tar_temp and cache['ACTORS'][a_indexes['Heater']]['state'] == True:
                        print('heat off')
                        cache['ACTORS'][a_indexes['Heater']]['state'] = False
                if 'Chiller' in a_indexes:
                    if cur_read > tar_temp + temp_tol and cache['ACTORS'][a_indexes['Chiller']]['state'] == False:
                        print('cool on')
                        cache['ACTORS'][a_indexes['Chiller']]['state'] = True
                    elif cur_read < tar_temp and cache['ACTORS'][a_indexes['Chiller']]['state'] == True:
                        print('cool off')
                        cache['ACTORS'][a_indexes['Chiller']]['state'] = False
                super().update_actors()
            except:
                print('Error running hysteresis loop on ' + vessel)
            socketio.sleep(sleep)
        x = 0
        for key, val in a_indexes.items():
            if cache['ACTORS'][val]['state'] == True:
                cache['ACTORS'][val]['state'] = False
            x =+ 1
        super().update_actors()
        a_msg = "Auto Control Terminated on " + vessel
        print(a_msg)
        socketio.emit('alert_warn', a_msg)