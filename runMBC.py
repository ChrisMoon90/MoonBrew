#!/usr/local/lib/python3.7
# -*- coding: utf-8 -*-

import flask
from flask_socketio import SocketIO, emit
import sensor_i2c
import time
from datetime import datetime, timedelta

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'MBC'
socketio = SocketIO(app)

#app.add_url_rule('/favicon.ico',redirect_to=url_for('static', filename='favicon.ico'))

#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://localhost:5432/flask_todo'
#db = SQLAlchemy(app)

device_list = sensor_i2c.get_devices()
active_i2c_devs = sensor_i2c.get_i2c_list(device_list)
print("Active I2C Devices: %s" % active_i2c_devs)

def RTD_Temp():
    print("Starting RTD Temp Background Process")
    last_save_time = datetime.now()
    while True:
        temps = {}
        temp_time = time.strftime("%H:%M:%S", time.localtime())
        temps['time'] = temp_time
        num_sensors = len(active_i2c_devs)
        for i in range(0, num_sensors):
            i2c_addr = active_i2c_devs[i]
            cur_temp = sensor_i2c.get_reading(device_list,i2c_addr)           
            temps[i] = cur_temp
        print("Temp Output: %s" % temps)
        socketio.emit('newtemps', temps)
        now = datetime.now()
        delta_time = now - last_save_time
        if now - timedelta(seconds=10) > last_save_time:
            save_to_file(temp_time, temps)
            last_save_time = datetime.now()
        socketio.sleep(1)

def save_to_file(temp_time, temps):
    filename = "./logs/Temps.log" #% (prefix, str(id))
    formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    msg = "%s, %s\n" % (formatted_time, temps)
    with open(filename, "a") as file:
        file.write(msg)
  
indexes = {'s0':0, 's1':1, 's2':2}
print(indexes)
@socketio.on('connect')
def MBC_connect():
    print('Client Connected')
    socketio.emit('connected',  {'connected': 'Connection Request Accepted'})
    socketio.emit('indexes', indexes)
   
@socketio.on('disconnect')
def MBC_disconnect():
    print('Client Disconnected')

@socketio.on('index_change')
def index_change(indexes_in):
    global indexes
    indexes = indexes_in
    print("Indexes from Client: %s" % indexes)
    
@app.route('/')
def index():
    try:      
        return flask.render_template('index.html')
    except ValueError:
            return str(e)


if __name__ == '__main__':     
    print("Starting Thread")
    thread = socketio.start_background_task(RTD_Temp)

    app.debug=False #setting to True will break this code! 
    socketio.run(app, host='192.168.0.31', port=5000)