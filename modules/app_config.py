print('Loading Config module...')

from aiohttp import web
from pprint import pprint
# import ssl
import socketio as sio
import os

from modules.sys_log import sys_log

# ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
# ssl_context.load_cert_chain('./certs/certificate.pem', './certs/key.pem')

socketio = sio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
app = web.Application()
socketio.attach(app)


# SET UP CACHE & CONFIG PARAMETERS ###################
global cache
cache = {           
        "INIT": [],
        "SENSORS":{},
        "ACTORS":{
            0:{},
            1:{},
            2:{},
            3:{}
            },
        "VESSELS":{
            'Boil_Kettle': {},
            'Mash_Tun': {},
            'Hot_Liquor_Tank': {},
            'Fermenter': {},
            'Smoker': {}
        },
        "SYSTEM": { 
            'Dynamic': {
                'log_state': False,
                'timer_start': 0
                },
            'AutoStates': {
                'Boil_Kettle': False,
                'Mash_Tun': False,
                'Hot_Liquor_Tank': False,
                'Fermenter': False,
                'Smoker': False
            }
        }
    }

def get_config_params(): 
    filename = "./config.txt"
    settings = ['Boil_Kettle', 'Mash_Tun', 'Hot_Liquor_Tank', 'Fermenter', 'Smoker']
    if os.path.exists(filename):
        pass
    else:
        print("Index file does not exist. Config file will be created.")
        with open(filename, 'w') as f:
            f.write("SYSTEM\n")
            f.write("'Static': {'version': '2.3.1', 'Mode': 'Brew', 'log_rate': 1}\n\n")
            a = {'Actors': {},
                'Sensors': {},
                'Params': {'tar_temp': 200, 'temp_tol': 2}}
            for i in settings:
                f.write(str(i) + '\n')
                for p in a:
                    f.write("'" + str(p) + "': " + str(a[p]) + '\n')
                f.write('\n')
    with open(filename, 'r+') as f:  # ADD TO CACHE
        x = 0
        cfile = f.readlines()          
        for line in cfile:
            for i in settings:
                if 'SYSTEM' in line:
                    static = eval('{' + str(cfile[x + 1]).rstrip("\n") + '}')
                    cache['SYSTEM']['Static'] = static['Static']
                    break
                elif i in line:
                    actors = cfile[x + 1].rstrip("\n")
                    sensors = cfile[x + 2].rstrip("\n")
                    params = cfile[x + 3].rstrip("\n")
                    set = eval('{' + actors + ', ' + sensors + ', ' + params + '}')
                    cache['VESSELS'][i] = set
            x += 1

async def update_config(dir, args):
    filename = "./config.txt"
    with open(filename, 'r') as f:
        cur_line = 0
        cfile = f.readlines()
        for line in cfile:
            cur_line +=1           
            if dir == 'SYSTEM':
                if dir in line:
                    dict = args[0]
                    cfile[cur_line] = "'Static': " + str(dict['Static']) + '\n'
            if dir == "VESSELS":
                if args[0] in line:
                    dict = args[1]
                    cfile[cur_line] = "'Actors': " + str(dict['Actors']) + '\n'
                    cfile[cur_line+1] = "'Sensors': " + str(dict['Sensors']) + '\n'
                    cfile[cur_line+2] = "'Params': " + str(dict['Params']) + '\n'
    with open(filename, 'w') as f:
        for i in range(0,len(cfile)):
            f.write(str(cfile[i]))

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
    await update_vessel(vessel, v_dict)

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
    cache['VESSELS'][args[0]] = args[1]
    await send_cache()
    await update_config('VESSELS', args) 
    pprint(cache)

get_config_params()


# CONNECTION FUNCTIONS ######################
@socketio.on('connect')
async def connect(sid, environ, auth):
    msg = 'Client Connected at SID: ' + sid
    sys_log(msg)
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