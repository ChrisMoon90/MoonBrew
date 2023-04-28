import pprint
import json

from modules.app_config import *
from modules.sensors import *
from modules.hardware import *
from modules.logging import *
from modules.controls import *


# CONNECTION FUNCTIONS ######################
@socketio.on('connected')
def connected():
    print('Client Connected!')
   
@socketio.on('disconnect')
def MBC_disconnect():
    print('Client Disconnected')


# CACHE FUNCTIONS ############################
@socketio.on('get_cache')
def get_cache():
    c.send_cache()

@socketio.on('system_update')
def update_system(s_dict):
    c.update_cache('SYSTEM', s_dict)

@socketio.on('vessel_update')
def update_vessel(vessel, v_dict):
    print('v_dict in: ')
    print(v_dict)
    c.update_cache('VESSELS', vessel, v_dict)

@socketio.on('add_rm_hardware')
def add_rm_hw(mod_type, vessel, hw_type):
    c.add_remove_hardware(mod_type, vessel, hw_type)


# # LOG FUNCTIONS ############################
# @socketio.on('fetch_log_state')
# def send_log_state():
#     l.send_fetched_log_state()

# @socketio.on('toggle_logState')
# def change_logState(logState_in):
#     l.toggle_logState(logState_in)

# @socketio.on('delete_log')
# def del_log():
#     l.delete_log()

# # TIMER FUNCTIONS ############################
# @socketio.on('fetch_timer')
# def send_start_time():
#     e.send_start_time()

# @socketio.on('start_timer')
# def start_timer():
#     e.start_timer()

# @socketio.on('reset_timer')
# def reset_timer():
#     e.reset_timer()


# CREATE MAIN API CLASSES #################
print("Creating API Classes")

c = CacheAPI()

t = SensorAPI()

# tftdi = ftdiAPI(t)

ti2c = i2cAPI(t)

l = logAPI(ti2c)

hw = hardwareAPI()

h = hysteresisAPI(ti2c, hw)

e = timerAPI()


# INITIALIZE BACKGROUND TASKS ###############
def initializer():
    for i in cache["INIT"]:
        args = []
        for key in i:
            if key == "function":
                function = i[key]
            else:
                arg = i[key]
                args.append(arg)
        thread = socketio.start_background_task(function, *args)


print("Starting Background Tasks")
initializer()

print("Full Compiled Cache")
pprint.pprint(cache)