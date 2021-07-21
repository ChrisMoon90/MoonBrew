from flask import redirect
from flask_socketio import emit
import threading
import os

from modules.app_config import *
import modules.ui
from modules.sensors import *


def get_db_indexes(): 
    indexes = {'s0':0, 's1':1, 's2':2}
    print(indexes)
    return indexes

@socketio.on('connect')
def MBC_connect():
    print('Client Connected')
    socketio.emit('connected',  {'connected': 'Connection Request Accepted'})
    #indexes = get_db_indexes()
    socketio.emit('indexes', indexes)
   
@socketio.on('disconnect')
def MBC_disconnect():
    print('Client Disconnected')

@socketio.on('index_change')
def index_change(indexes_in):
    global indexes
    indexes = indexes_in
    socketio.emit('indexes', indexes)
    print("Indexes Received from Client & Broadcasted: %s" % indexes)
    
@socketio.on('delete_log')
def delete_log():
    print("Deleting Temp.log File")
    filename = "./logs/Temps.log"
    if os.path.exists(filename):
      os.remove(filename)
    else:
      print("The file does not exist")
       
@app.route('/')
def index0():
    try:      
        return redirect('/ui')
    except ValueError:
            return str(e)
   
print("Starting Threads")
thread = socketio.start_background_task(target=RTD_Temp, sleep = 0)
thread2 = socketio.start_background_task(target=save_to_file, sleep = 15)

indexes = get_db_indexes()