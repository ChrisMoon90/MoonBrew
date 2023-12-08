print('Loading System module...')

import os
from modules.app_config import socketio

async def delete_log(path):   
    if os.path.exists(path):
        os.remove(path)
        a_msg = "Log File Successfully Deleted"
        print(a_msg)
        await socketio.emit('alert_success', a_msg)
    else:
        a_msg = "Log File not Deleted: file does not exist"
        print(a_msg)
        await socketio.emit('alert_warn', a_msg)


# SYSTEM SOCKETIO FUNCTIONS ############################
@socketio.on('delete')
async def del_log(sid, target):
    await delete_log('./logs/' + target)

@socketio.on('reboot')
async def restart(sid):
    print('Rebooting System')
    await socketio.sleep(2)
    return os.system("reboot")