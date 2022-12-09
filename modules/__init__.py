# from flask import redirect
# from flask_socketio import emit

from modules.app_config import *
from modules.cache import *
import modules.ui
from modules.sensors.i2c import *
from modules.hardware import *
from modules.logging import *
from modules.controls import *


# CONNECTION FUNCTIONS ######################
@socketio.on('connect')
def MlC_connect():
    print('Client Connected')
    socketio.emit('connected',  {'connected': 'Connection Request Accepted'})
   
@socketio.on('disconnect')
def MlC_disconnect():
    print('Client Disconnected')


# TEMP FUNCTIONS ############################
# @socketio.on('fetch_temps')
# def send_temps():
#     a.emit_temp()

@socketio.on('fetch_temp_indexes')
def send_temp_indexes():
    ti2c.send_temp_indexes()

@socketio.on('temp_index_change')
def mod_temp_index(temp_indexes_in):
    ti2c.temp_index_change(temp_indexes_in)


# FAN FUNCTIONS ############################
@socketio.on('fetch_fan_indexes')
def send_fan_indexes():
    hw.send_fan_indexes()

@socketio.on('fetch_fan_states')
def send_fan_states():
    hw.send_fan_states()
    
@socketio.on('fan_index_change')
def change_fan_index(fan_indexes_in):
    hw.fan_index_change(fan_indexes_in)

@socketio.on('toggle_fan_state')
def change_fan_state(fanID, fan_state):
    hw.toggle_fan_state(fanID, fan_state)


# HYSTERESIS CONTROL FUNCTIONS ########################
@socketio.on('fetch_auto_state')
def send_auto_state():
    h.send_auto_state()

@socketio.on('toggle_auto_state')
def change_auto_state():
    h.toggle_auto_state()

@socketio.on('Fetch_TarTemp')
def fetch_target_temp():
    h.fetch_tar_temp()

@socketio.on('TarTemp_Update')
def update_target_temp(tar_temp):
    h.set_tar_temp(tar_temp)

@socketio.on('Fetch_TempTol')
def get_temp_tol():
    h.fetch_temp_tol()

@socketio.on('ToggleTempTol')
def update_temp_tol(temp_tol):
    h.set_temp_tol(temp_tol)


# LOG FUNCTIONS ############################
@socketio.on('fetch_log_state')
def send_log_state():
    l.send_fetched_log_state()

@socketio.on('toggle_logState')
def change_logState(logState_in):
    l.toggle_logState(logState_in)

@socketio.on('delete_log')
def del_log():
    l.delete_log()

# TIMER FUNCTIONS ############################
@socketio.on('fetch_timer')
def send_start_time():
    e.send_start_time()

@socketio.on('start_timer')
def start_timer():
    e.start_timer()

@socketio.on('reset_timer')
def reset_timer():
    e.reset_timer()




# CREATE MAIN API CLASSES #################
print("Creating API Classes")

c = CacheAPI()

ti2c = i2cAPI(c)

l = logAPI(ti2c)

hw = fanAPI(c)

h = hysteresisAPI(ti2c, hw)

e = timerAPI()