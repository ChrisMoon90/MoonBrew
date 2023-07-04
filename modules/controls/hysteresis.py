from pprint import pprint

from modules.actors.__init__ import ActorAPI
from modules.app_config import socketio, cache


class HysteresisAPI(ActorAPI):

    def __init__(self):
        for key, val in cache['SYSTEM']['AutoStates'].items():
            setattr(self, key, val)
        pprint(vars(self))

    def update_auto_states(self):
        for key, val in cache['SYSTEM']['AutoStates'].items(): 
            if val == True:
                if getattr(self, key) == False:   
                    setattr(self, key, val)                                 
                    thread = socketio.start_background_task(target=self.hysteresis, vessel = key, sleep = 2)                  
            setattr(self, key, val) 

    def hysteresis(self, vessel, sleep):
        a_msg = "Auto Control Started on " + vessel
        print(a_msg)
        socketio.emit('alert_success', a_msg)
        v_dict = cache['VESSELS'][vessel]
        while getattr(self, vessel):
            a_indexes = []
            for key in v_dict['Actors']:
                if key >= 2:
                    pass
                else:
                    a_indexes.append(v_dict['Actors'][key]['index'])
            cur_read = cache['SENSORS'][v_dict['Sensors'][0]['index']]['cur_read']
            tar_temp = v_dict['Params']['tar_temp']
            temp_tol = v_dict['Params']['temp_tol']
            try:
                if len(a_indexes) >= 1:
                    if cur_read < tar_temp - temp_tol and cache['ACTORS'][a_indexes[0]]['state'] == False:
                        print('heat on', a_indexes[0])
                        cache['ACTORS'][a_indexes[0]]['state'] == True
                    elif cur_read > tar_temp and cache['ACTORS'][a_indexes[0]]['state'] == True:
                        print('heat off')
                        cache['ACTORS'][a_indexes[0]]['state'] == False
                if len(a_indexes) > 1:
                    if cur_read > tar_temp + temp_tol and cache['ACTORS'][a_indexes[1]]['state'] == False:
                        print('cool on')
                        cache['ACTORS'][a_indexes[0]]['state'] == True
                    elif cur_read < tar_temp and cache['ACTORS'][a_indexes[1]]['state'] == True:
                        print('cool off')
                        cache['ACTORS'][a_indexes[0]]['state'] == False
                super().upadte_actors() 
            except:
                print('Error running hysteresis loop on ' + vessel)
            socketio.sleep(sleep)
        x = 0
        for i in a_indexes:
            if cache['ACTORS'][i]['state'] == True:
                cache['ACTORS'][i]['state'] == False
            x =+ 1
        super().update_actors()
        a_msg = "Auto Control Terminated on " + vessel
        print(a_msg)
        socketio.emit('alert_warn', a_msg)