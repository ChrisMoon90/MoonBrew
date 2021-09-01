from flask import redirect
from flask_socketio import emit
import os

from modules.app_config import *
import modules.ui
from modules.sensors import *


def get_config_indexes(): 
    filename = "./config.txt"
    if os.path.exists(filename):
        with open(filename, 'r+') as f:
            cur_line = 0
            cfile = f.readlines()
            for x in cfile:
                cur_line += 1
                if "Temp_Indexes" in x:
                    temp_indexes_raw = cfile[cur_line].rstrip("\n")
                if "Fan_Indexes" in x:
                    fan_indexes_raw = cfile[cur_line]        
            temp_indexes = eval(temp_indexes_raw)
            fan_indexes = eval(fan_indexes_raw)
    else:
        print("Index file does not exist. Config file will be created.")
        temp_indexes = {'s0':0, 's1':1, 's2':2}
        fan_indexes = {'f0':0, 'f1':1, 'f2':2}
        with open(filename, 'w') as f:
            f.write("Temp_Indexes\n")
            f.write(str(temp_indexes) + "\n\n")
            f.write("Fan_Indexes\n")
            f.write(str(fan_indexes))
    print("Config_temp_indexes: ", temp_indexes)
    print("Config fan_indexes: ", fan_indexes)
    indexes = [temp_indexes, fan_indexes]
    return indexes

@socketio.on('connect')
def MBC_connect():
    print('Client Connected')
    socketio.emit('connected',  {'connected': 'Connection Request Accepted'})
    indexes = get_config_indexes()
    socketio.emit('temp_indexes', indexes[0])
    socketio.emit('fan_indexes', indexes[1])
    socketio.emit('logState', b.running)
   
@socketio.on('disconnect')
def MBC_disconnect():
    print('Client Disconnected')

@socketio.on('temp_index_change')
def temp_index_change(temp_indexes_in):
    temp_indexes = temp_indexes_in
    filename = "./config.txt"
    with open(filename, 'r') as f:
        cur_line = 0
        cfile = f.readlines()
        for line in cfile:
            cur_line +=1
            if "Temp_Indexes" in line:
                cfile[cur_line] = str(temp_indexes) + '\n'
    with open(filename, 'w') as f:
        for i in range(0,len(cfile)):
            f.write(str(cfile[i]))
    socketio.emit('temp_indexes', temp_indexes)
    print("Temp_Indexes Received from Client & Broadcasted: %s" % temp_indexes)

@socketio.on('fan_index_change')
def fan_change(fan_indexes_in):
    fan_indexes = fan_indexes_in
    filename = "./config.txt"
    with open(filename, 'r') as f:
        cur_line = 0
        cfile = f.readlines()
        for line in cfile:
            cur_line +=1
            if "Fan_Indexes" in line:
                cfile[cur_line] = str(fan_indexes) + '\n'
    with open(filename, 'w') as f:
        for i in range(0,len(cfile)):
            f.write(str(cfile[i]))         
    socketio.emit('fan_indexes', fan_indexes)
    print("Fan_Indexes Received from Client & Broadcasted: %s" % fan_indexes)
    
@socketio.on('toggle_logState')
def toggle_logState(logState_in):
    logState = not logState_in
    b.set_run_state(logState)
    if logState == True:
        thread2 = socketio.start_background_task(target=b.save_to_file, sleep = 15)
    else:
        print("Stopping Logging Thread") 
    socketio.emit('logState', logState)

@socketio.on('delete_log')
def delete_log():   
    filename = "./logs/Temps.log"
    if os.path.exists(filename):
      os.remove(filename)
      msg = "Temp Log File Successfully Deleted"
      print(msg)
      socketio.emit('log_deleted', msg)
    else:
      print("The file does not exist")
       
@app.route('/')
def index0():
    try:      
        return redirect('/ui')
    except ValueError:
            return str(e)


print("Starting Temp Thread")
a = tempAPI()
device_list = a.get_devices()
active_i2c_devs = a.get_i2c_list(device_list)
print("Active I2C Devices: %s" % active_i2c_devs)
thread1 = socketio.start_background_task(target=a.RTD_Temp, dev_list=device_list, active_devs=active_i2c_devs, sleep=2)

b = logAPI(a)