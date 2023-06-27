from pprint import pprint

from modules.app_config import socketio, cache


class hysteresisAPI:

    def __init__(self):
        for key, val in cache['SYSTEM']['AutoStates'].items():
            setattr(self, key, val)
        pprint(vars(self))

    def update_auto_states(self, hw):
        for key, val in cache['SYSTEM']['AutoStates'].items(): 
            if val == True:
                if getattr(self, key) == False:   
                    setattr(self, key, val)                                 
                    thread = socketio.start_background_task(target=self.hysteresis, hw = hw, vessel = key, sleep = 2)                  
            setattr(self, key, val) 

    def hysteresis(self, hw, vessel, sleep):
        a_msg = "Auto Control Started on " + vessel
        print(a_msg)
        socketio.emit('alert_success', a_msg)
        v_dict = cache['VESSELS'][vessel]
        a_indexes = []
        print(getattr(self, vessel))
        while getattr(self, vessel):
            for key in v_dict['Actors']:
                if key >= 2:
                    pass
                else:
                    a_indexes.append(v_dict['Actors'][key]['index'])
            cur_read = cache['SENSORS'][v_dict['Sensors'][0]['index']]['cur_read']
            tar_temp = v_dict['Params']['tar_temp']
            temp_tol = v_dict['Params']['temp_tol']
            try:
                if cur_read < tar_temp - temp_tol and cache['ACTORS'][a_indexes[0]]['state'] == False:
                        hw.toggle_actor_state(a_indexes[0]) 
                elif cur_read > tar_temp and cache['ACTORS'][a_indexes[0]]['state'] == True:
                        hw.toggle_actor_state(a_indexes[0])
                if cur_read > tar_temp + temp_tol and cache['ACTORS'][a_indexes[1]]['state'] == False:
                        hw.toggle_actor_state(a_indexes[1]) 
                elif cur_read < tar_temp and cache['ACTORS'][a_indexes[1]]['state'] == True:
                        hw.toggle_actor_state(a_indexes[1])
            except:
                print('Error running hysteresis loop on ' + vessel)
            socketio.sleep(sleep)
        for i in a_indexes:
            if cache['ACTORS'][i]['state'] == True:
                hw.toggle_actor_state(a_indexes[i])
        a_msg = "Auto Control Terminated on " + vessel
        print(a_msg)
        socketio.emit('alert_warn', a_msg)