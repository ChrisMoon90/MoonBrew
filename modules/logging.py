print('Loading Logging module...')

import time
import os

from modules.app_config import socketio, cache
from modules.cache import update_cache


class logAPI:

    run_state = False
    log_rate = cache['SYSTEM']['Static']['log_rate']
    filename = "./logs/Sensors.csv"

    async def set_log_rate():
        logAPI.log_rate = cache['SYSTEM']['Static']['log_rate']

    async def set_log_state():
        logAPI.run_state = cache['SYSTEM']['Dynamic']['log_state']
        if logAPI.run_state:
            t = socketio.start_background_task(target = logAPI.save_to_file)
        else:
            a_msg = 'Logging Stopped'
            print(a_msg)
            await socketio.emit('alert_warn', a_msg)

    async def save_to_file():
        a_msg = 'Logging Corountine Started...'
        print(a_msg)
        await socketio.emit('alert_success', a_msg)
        while logAPI.run_state: 
            try:
                await logAPI.set_log_rate()
                log_rate = logAPI.log_rate * 60
                ft = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                r = []
                for i in cache['SENSORS']:
                    r.append(cache['SENSORS'][i]['cur_read'])
                msg = ft
                for x in r:
                    val = "%.3f" % x
                    msg += ', ' + val
                print("Saving to File: %s" % msg)
                if os.path.exists(logAPI.filename):
                    with open(logAPI.filename, "a") as f:
                        f.write("%s\n" % msg)
                else:
                    print("Temp.csv file does not exist. File will be created.")
                    header = "Time, Sensor 1, Sensor 2, Sensor 3, Sensor 4, Sensor 5, Sensor 6\n"
                    with open(logAPI.filename, 'a') as f:
                        f.write(header)
                        f.write("%s\n" % msg)
            except:
                print('Logging Error')
            await socketio.sleep(log_rate)
        print('Logging Coroutine Exited')


    async def delete_log():   
        if os.path.exists(logAPI.filename):
            os.remove(logAPI.filename)
            a_msg = "Log File Successfully Deleted"
            print(a_msg)
            await socketio.emit('alert_success', a_msg)
        else:
            a_msg = "Log File not Deleted: file does not exist"
            print(a_msg)
            await socketio.emit('alert_warn', a_msg)


# LOG SOCKETIO FUNCTIONS ############################
@socketio.on('set_log_state')
async def set_log_state(sid, s_dict):
    await update_cache('SYSTEM', s_dict)
    await logAPI.set_log_state()

@socketio.on('delete_log')
async def del_log(sid):
    await logAPI.delete_log()