#!/usr/local/lib/python3.7
# -*- coding: utf-8 -*-

import flask
from flask_socketio import SocketIO, emit
import sensor_i2c
import time

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'MBC'
socketio = SocketIO(app)

#app.add_url_rule('/favicon.ico',redirect_to=url_for('static', filename='favicon.ico'))

#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://localhost:5432/flask_todo'
#db = SQLAlchemy(app)

device_list = sensor_i2c.get_devices()
active_i2c_devs = sensor_i2c.get_i2c_list(device_list)
print(active_i2c_devs)

def RTD_Temp():
    print("Starting RTD Temp Background Process")  
    while True:
        temps = {}
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        temps['time'] = current_time
        num_sensors = len(active_i2c_devs)
        for i in range(0, num_sensors):
            i2c_addr = active_i2c_devs[i]
            cur_temp = sensor_i2c.get_reading(device_list,i2c_addr)           
            temps[i] = cur_temp
        print("Temp Output: %s" % temps)
        socketio.emit('newtemps', temps)
        socketio.sleep(2)
      
@socketio.on('connect')
def MBC_connect():
    print('Client Connected')
    socketio.emit('connected',  {'connected': 'Connection Request Accepted'})
   
@socketio.on('disconnect')
def MBC_disconnect():
    print('Client Disconnected')
    
@socketio.on('message')
def handleMessage(msg):
    print('Message: %s' % msg)
    #send(msg, broadcast=True)
    
@socketio.on('sensor_change')
def change_sensor1(index):
    print("Smoker sensor changed to: %s" % index)
    
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