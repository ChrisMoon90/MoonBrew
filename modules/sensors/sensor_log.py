print('Loading Sensor Logging module...')

from datetime import datetime
import os

from modules.app_config import socketio, cache, update_config, convert_strings
from modules.sys_log import sys_log


class logAPI:

    run_state = False
    log_rate = cache['SYSTEM']['Static']['log_rate']
    t = datetime.now()
    last_send = t.replace(year=1990, month=12, day=25, hour=10, minute=30, second=0)
    dir = "./logs/"
    fn = "sensors.csv"

    async def update_sys_log_state(s_dict): 
        args = await convert_strings(s_dict)    
        cache['SYSTEM'] = args[0]
        await socketio.emit('log_update', cache)
        await update_config('SYSTEM', args) 

    async def set_log_rate():
        logAPI.log_rate = cache['SYSTEM']['Static']['log_rate']

    async def set_log_state():
        logAPI.run_state = cache['SYSTEM']['Dynamic']['log_state']
        if logAPI.run_state:
            t = socketio.start_background_task(target = logAPI.save_to_file)
        else:
            a_msg = 'Sensor Logging Stopped'
            await socketio.emit('alert_warn', a_msg)

    async def get_cur_data():
        r = []
        for i in cache['SENSORS']:
            r.append(cache['SENSORS'][i]['cur_read'])
        msg = str(datetime.now())
        for x in r:
            msg += ', ' + str(x)
        return msg

    async def save_to_file():
        a_msg = 'Sensor Logging Started'
        await socketio.emit('alert_success', a_msg)
        sys_log(a_msg)
        while logAPI.run_state: 
            try:
                await logAPI.set_log_rate()
                now = datetime.now()
                delta = now - logAPI.last_send
                if delta.total_seconds() >= logAPI.log_rate * 60:
                    msg = await logAPI.get_cur_data()               
                    print("Saving to File: %s" % msg)
                    if os.path.exists(logAPI.dir + logAPI.fn):
                        with open(logAPI.dir + logAPI.fn, "a") as f:
                            f.write("%s\n" % msg)
                    else:
                        print("sensors.csv file does not exist. File will be created.")
                        if os.path.isdir(logAPI.dir):
                            pass
                        else:
                            os.mkdir(logAPI.dir)
                        header = "Time, Sensor 1, Sensor 2, Sensor 3, Sensor 4, Sensor 5, Sensor 6\n"
                        with open(logAPI.dir + logAPI.fn, 'a') as f:
                            f.write(header)
                            f.write("%s\n" % msg)
                    logAPI.last_send = now
                    await socketio.emit('sensor_log_update')
            except Exception as e:
                sys_log('Logging Error: ' + str(e))
            await socketio.sleep(1)
        t = datetime.now()
        logAPI.last_send = t.replace(year=1990, month=12, day=25, hour=10, minute=30, second=0)
        sys_log('Sensor logging coroutine exited')


# SENSOR LOG SOCKETIO FUNCTIONS ############################
@socketio.on('set_log_state')
async def set_log_state(sid, s_dict):
    await logAPI.update_sys_log_state(s_dict)
    await logAPI.set_log_state()