print('Loading System module...')

import os
from pprint import pprint

from modules.app_config import socketio, cache, update_config, convert_strings, send_cache
from modules.sys_log import sys_log
# from modules.cache import convert_strings, send_cache
from modules.controls.hysteresis import HysteresisAPI
from modules.sensors.ftdi import re_init_ftdi
from modules.sensors.tilt import tilt_init


async def delete_log(target): 
    path = './logs/' + target  
    if os.path.exists(path):
        os.remove(path)
        a_msg = "File Successfully Deleted: " + target
        print(a_msg)
        await socketio.emit('alert_success', a_msg)
    else:
        a_msg = 'File not Deleted: ' + target + ' File Does Not Exist'
        print(a_msg)
        await socketio.emit('alert_warn', a_msg)

async def update_system(s_dict): 
    args = await convert_strings(s_dict)    
    cache['SYSTEM'] = args[0]
    await HysteresisAPI.update_auto_states()
    await send_cache()
    await update_config('SYSTEM', args) 
    pprint(cache)

async def sensor_init():
    sys_log('Re-Initializing Sensors...')
    # await re_init_ftdi()
    await tilt_init()


# SYSTEM SOCKETIO FUNCTIONS ############################
@socketio.on('system_update')
async def system_update(sid, s_dict): 
    await update_system(s_dict)

@socketio.on('delete')
async def del_log(sid, target):
    await delete_log(target)

@socketio.on('init_sensors')
async def init_sensors(sid):
    print('Re-Initializing Sensors')
    await sensor_init()

@socketio.on('reboot')
async def restart(sid):
    print('Rebooting System')
    await socketio.sleep(2)
    return os.system("reboot")