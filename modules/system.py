print('Loading System module...')

import os
from modules.app_config import socketio
from modules.sys_log import sys_log
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

async def sensor_init():
    sys_log('Re-Initializing Sensors...')
    # await re_init_ftdi()
    await tilt_init()


# SYSTEM SOCKETIO FUNCTIONS ############################
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