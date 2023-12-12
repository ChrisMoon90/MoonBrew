print('Loading System module...')

import os
from modules.app_config import socketio

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


# SYSTEM SOCKETIO FUNCTIONS ############################
@socketio.on('delete')
async def del_log(sid, target):
    await delete_log(target)

@socketio.on('reboot')
async def restart(sid):
    print('Rebooting System')
    await socketio.sleep(2)
    return os.system("reboot")