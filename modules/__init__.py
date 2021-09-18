# from flask import redirect
# from flask_socketio import emit

from modules.app_config import *
import modules.ui
from modules.sensors import *
from modules.hardware import *
from modules.logging import *
from modules.controls import *


# CONNECTION FUNCTIONS ######################
@socketio.on('connect')
def MBC_connect():
    print('Client Connected')
    socketio.emit('connected',  {'connected': 'Connection Request Accepted'})
   
@socketio.on('disconnect')
def MBC_disconnect():
    print('Client Disconnected')


# TEMP FUNCTIONS ############################
@socketio.on('fetch_temps')
def send_temps():
    a.emit_temp()

@socketio.on('fetch_temp_indexes')
def send_temp_indexes():
    a.send_temp_indexes()

@socketio.on('temp_index_change')
def mod_temp_index(temp_indexes_in):
    a.temp_index_change(temp_indexes_in)


# FAN FUNCTIONS ############################
@socketio.on('fetch_fan_indexes')
def send_fan_indexes():
    c.send_fan_indexes()

@socketio.on('fetch_fan_states')
def send_fan_states():
    c.send_fan_states()
    
@socketio.on('fan_index_change')
def change_fan_index(fan_indexes_in):
    c.fan_index_change(fan_indexes_in)

@socketio.on('toggle_fan_state')
def change_fan_state(fanID, fan_state):
    c.toggle_fan_state(fanID, fan_state)


# CONTROL FUNCTIONS ########################
@socketio.on('fetch_auto_state')
def send_auto_state():
    d.send_auto_state()

@socketio.on('toggle_auto_state')
def change_auto_state():
    d.toggle_auto_state()

@socketio.on('Fetch_TarTemp')
def fetch_target_temp():
    d.fetch_tar_temp()

@socketio.on('TarTemp_Update')
def update_target_temp(tar_temp):
    d.set_tar_temp(tar_temp)

@socketio.on('Fetch_TempTol')
def get_temp_tol():
    d.fetch_temp_tol()

@socketio.on('ToggleTempTol')
def update_temp_tol(temp_tol):
    d.set_temp_tol(temp_tol)


# LOG FUNCTIONS ############################
@socketio.on('fetch_log_state')
def send_log_state():
    b.send_fetched_log_state()

@socketio.on('toggle_logState')
def change_logState(logState_in):
    b.toggle_logState(logState_in)

@socketio.on('delete_log')
def del_log():
    b.delete_log()


# CREATE MAIN API CLASSES #################
print("Creating API Classes")

a = tempAPI()

b = logAPI(a)

c = fanAPI()

d = hysteresisAPI(a, c)