print('Loading Cache Module...')

from pprint import pprint

from modules.app_config import socketio, cache, update_config


async def send_cache():
    cache_emit = cache
    try: 
        del cache_emit['INIT']
    except:
        pass
    await socketio.emit('cache', cache_emit)

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
    await update_vessel('VESSELS', vessel, v_dict)

async def convert_strings(*args):
    args_out = []
    for r in args:
        if type(r) is dict:
            f = dfilter(r)
        else:
            f = r
        args_out.append(f)
    return args_out

def dfilter(d):
    d_new = {}
    for key, val in d.items():
        try:
            i_key = int(key)
        except:
            i_key = key
        d_new[i_key] = val
    for key, val in d_new.items():
        if type(val) is dict:
            d_new[key] = dfilter(val)
        else:
            if val == True or val == False:
                pass
            else:
                try:
                    if float(val) > int(float(val)):
                        d_new[key] = float(val)
                    else:
                        d_new[key] = int(float(val))
                except:
                    pass
    return d_new

async def update_vessel(*args):
    args = await convert_strings(*args) 
    pprint(args[0])
    pprint(args[1])   
    cache['VESSELS'][args[0]] = args[1]
    await send_cache()
    await update_config(dir, args) 
    pprint(cache)


# CONNECTION FUNCTIONS ######################
@socketio.on('connect')
async def connect(sid, environ, auth):
    print('Client Connected at SID: ', sid)
    await send_cache()
   
@socketio.on('disconnect')
async def MBC_disconnect(sid):
    print('Client Disconnected SID: ', sid)


# CACHE FUNCTIONS ##############################
@socketio.on('get_cache')
async def get_cache(sid):
    await send_cache()

@socketio.on('vessel_update')
async def vessel_update(sid, *args):
    await update_vessel(*args)

@socketio.on('add_rm_hardware')
async def add_rm_hw(sid, mod_type, vessel,  hw_type):
    await add_remove_hardware(mod_type, vessel, hw_type)