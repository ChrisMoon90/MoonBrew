print('Loading Cache Module...')

from pprint import pprint
from modules.controls.hysteresis import HysteresisAPI
from modules.app_config import socketio, cache, update_config

class CacheAPI(HysteresisAPI):

    def __init__(self):
        self.cache = cache

    def cache_update(self):
        self.cache = cache

    def send_cache(self):
        cache_emit = self.cache
        try: 
            del cache_emit['INIT']
        except:
            pass
        socketio.emit('cache', cache_emit)

    def update_cache(self, dir, *args):
        args = self.convert_strings(*args) 
        if dir == "ACTORS":
            self.cache[dir] = args[0]
            super().update_actors()
        else:         
            if dir == 'SYSTEM':          
                self.cache[dir] = args[0]
                super().update_auto_states()
            if dir == 'VESSELS':
                self.cache[dir][args[0]] = args[1]
                self.send_cache()
        update_config(dir, *args)       
        pprint.pprint(self.cache)

    def add_remove_hardware(self, mod_type, vessel, hw_type):
        v_dict = self.cache['VESSELS'][vessel]
        count = len(v_dict[hw_type])
        if mod_type == "add":
            if hw_type == "Actors":
                print("Adding Actor to ", vessel)
                v_dict[hw_type][int(count)] = {'name': 'Actor1', 'index': 0, 'type': 'Pump'}
            else:
                print("Adding Sensor to ", vessel)
                v_dict[hw_type][int(count)] = {'name': 'Temp', 'index': 0}
        else:
            print("Deleting " + hw_type + ' from ' + vessel)
            del v_dict[hw_type][int(count - 1)]
        self.update_cache('VESSELS', vessel, v_dict)

    def convert_strings(self, *args):
        args_out = []
        for r in args:
            if type(r) is dict:
                for x in self.dfilter(r):
                    r = x
            args_out.append(r)
        return args_out

    def dfilter(self, d):
        for key, val in d.items():
            try:
                if type(key) is int:
                    pass
                else:
                    d[int(key)] = val
                    del d[key]
            except:
                pass
            if type(val) is dict:
                yield from self.dfilter(val)
            else:
                if val == True or val == False:
                    pass
                else:
                    try:
                        if float(val) > int(float(val)):
                            d[key] = float(val)
                        else:
                            d[key] = int(float(val))
                    except:
                        d[key] = val
        yield d


# CACHE FUNCTIONS ############################
@socketio.on('get_cache')
def get_cache():
    CacheAPI.send_cache()

@socketio.on('system_update')
def update_system(s_dict):
    CacheAPI.update_cache('SYSTEM', s_dict)

@socketio.on('vessel_update')
def update_vessel(vessel, v_dict):
    CacheAPI.update_cache('VESSELS', vessel, v_dict)

@socketio.on('add_rm_hardware')
def add_rm_hw(mod_type, vessel,  hw_type):
    CacheAPI.add_remove_hardware(mod_type, vessel, hw_type)

@socketio.on('actor_update')
def actor_update(a_dict):
    CacheAPI.update_cache('ACTORS', a_dict)