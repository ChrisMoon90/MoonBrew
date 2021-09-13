from flask import redirect
from flask_socketio import emit
#import os

from modules.app_config import *
import modules.ui
from modules.sensors import *
from modules.hardware import *
from modules.logging import *


@socketio.on('connect')
def MBC_connect():
    print('Client Connected')
    socketio.emit('connected',  {'connected': 'Connection Request Accepted'})
   
@socketio.on('disconnect')
def MBC_disconnect():
    print('Client Disconnected')

@socketio.on('fetch_temp_indexes')
def send_temp_indexes():
    indexes = modules.app_config.get_config_indexes()
    socketio.emit('temp_indexes', indexes[0])

@socketio.on('fetch_fan_indexes')
def send_fan_indexes():
    indexes = modules.app_config.get_config_indexes()
    socketio.emit('fan_indexes', indexes[1])

@socketio.on('fetch_temps')
def send_temps():
    a.emit_temp()

@socketio.on('fetch_log_state')
def send_log_state():
    socketio.emit('logState', b.running)

@socketio.on('temp_index_change')
def mod_temp_index(temp_indexes_in):
    a.temp_index_change(temp_indexes_in)

@socketio.on('fetch_fan_states')
def send_fan_states():
    c.send_fan_states()
    
@socketio.on('fan_index_change')
def change_fan_index(fan_indexes_in):
    c.fan_index_change(fan_indexes_in)

@socketio.on('toggle_fan_state')
def change_fan_state(fanID):
    c.toggle_fan_state(fanID)
    
@socketio.on('toggle_logState')
def change_logState(logState_in):
    b.toggle_logState(logState_in)

@socketio.on('delete_log')
def del_log():
    b.delete_log()
       

#START MAIN THREADS
print("Starting Threads")

a = tempAPI()

device_list = a.get_devices()
active_i2c_devs = a.get_i2c_list(device_list)
print("Active I2C Devices: %s" % active_i2c_devs)
thread1 = socketio.start_background_task(target=a.RTD_Temp, dev_list=device_list, active_devs=active_i2c_devs, sleep=2)

b = logAPI(a)

c = hardwareAPI()