from flask import redirect
from flask_socketio import emit
import threading
import os

from modules.app_config import *
import modules.ui
from modules.sensors import *


def get_db_indexes(): 
    filename = "./logs/indexes.log"
    if os.path.exists(filename):
        with open(filename) as f:
            indexes_raw = f.readlines()
            indexes = eval(indexes_raw[0])
    else:
        print("Index file does not exist. Index file will be created.")
        indexes = {'s0':0, 's1':1, 's2':2}
        with open(filename, 'w') as f:
                f.write(str(indexes))
    print("db_indexes: ", indexes)
    return indexes

@socketio.on('connect')
def MBC_connect():
    print('Client Connected')
    socketio.emit('connected',  {'connected': 'Connection Request Accepted'})
    indexes = get_db_indexes()
    socketio.emit('indexes', indexes)
    socketio.emit('logState', b.running)
   
@socketio.on('disconnect')
def MBC_disconnect():
    print('Client Disconnected')

@socketio.on('index_change')
def index_change(indexes_in):
    indexes = indexes_in
    filename = "./logs/indexes.log"
    with open(filename, 'w') as f:
        f.truncate()
        f.write(str(indexes))
    socketio.emit('indexes', indexes)
    print("Indexes Received from Client & Broadcasted: %s" % indexes)
    
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
thread1 = socketio.start_background_task(target=a.RTD_Temp, sleep = 2)

b = logAPI(a)