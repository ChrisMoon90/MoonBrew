print('Loading Cache Module...')

from pprint import pprint

from modules.controls.hysteresis import HysteresisAPI
from modules.controls.actors import ActorAPI
from modules.app_config import socketio, cache, update_config


async def send_cache():
    cache_emit = cache
    try: 
        del cache_emit['INIT']
    except:
        pass
    await socketio.emit('cache', cache_emit)

async def update_cache(dir, *args):
    args = await convert_strings(*args) 
    if dir == "ACTORS":
        cache[dir] = args[0]
        await ActorAPI.update_actors()
    else:         
        if dir == 'SYSTEM':          
            cache[dir] = args[0]
            await HysteresisAPI.update_auto_states()
        if dir == 'VESSELS':
            cache[dir][args[0]] = args[1]
    await send_cache()
    await update_config(dir, *args)       
    pprint(cache)

async def add_remove_hardware(mod_type, vessel, hw_type):
    v_dict = cache['VESSELS'][vessel]
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
    await update_cache('VESSELS', vessel, v_dict)

async def convert_strings(*args):
    args_out = []
    for r in args:
        if type(r) is dict:
            for x in dfilter(r):
                r = x
        args_out.append(r)
    return args_out

def dfilter(d):
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
            yield from dfilter(val)
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


# CONNECTION FUNCTIONS ######################
@socketio.on('connected')
async def connected(sid):
    print('Client Connected at SID: ', sid)
    await send_cache()
   
@socketio.on('disconnect')
async def MBC_disconnect(sid):
    print('Client Disconnected SID: ', sid)


# CACHE FUNCTIONS ##############################
@socketio.on('get_cache')
async def get_cache(sid):
    await send_cache()

@socketio.on('system_update')
async def update_system(sid, s_dict):
    await update_cache('SYSTEM', s_dict)

@socketio.on('vessel_update')
async def update_vessel(sid, vessel, v_dict):
    await update_cache('VESSELS', vessel, v_dict)

@socketio.on('add_rm_hardware')
async def add_rm_hw(sid, mod_type, vessel,  hw_type):
    await add_remove_hardware(mod_type, vessel, hw_type)

@socketio.on('actor_update')
async def actor_update(sid, a_dict):
    await update_cache('ACTORS', a_dict)
