#!/usr/local/lib/python3.7
# -*- coding: utf-8 -*-

import flask
from flask_socketio import SocketIO, emit
from random import random
from time import sleep
from threading import Thread, Event
import sensors

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'MBC'
socketio = SocketIO(app)

#app.add_url_rule('/favicon.ico',redirect_to=url_for('static', filename='favicon.ico'))

#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://localhost:5432/flask_todo'
#db = SQLAlchemy(app)

thread = Thread()
thread2 = Thread()
thread_stop_event = Event()
thread_stop_event2 = Event()

def RTD_Temp1():
    print("Starting RTD Temp Process 1")
    sensor1 = sensors.get_sensor(0)
    while not thread_stop_event.isSet():
        temp1 = sensors.run_Temp(sensor1)
        print("Temp1 = ", temp1)
        temp1_out = temp1, " °F"
        socketio.emit('newtemp1', {'temp1': temp1_out})
        socketio.sleep(2)

def RTD_Temp2():
    print("Starting RTD Temp Process 2")
    sensor2 = sensors.get_sensor(1)
    while not thread_stop_event.isSet():
        temp2 = sensors.run_Temp(sensor2)
        print("Temp2 = ", temp2)
        temp2_out = temp2, " °F"
        socketio.emit('newtemp2', {'temp2': temp2_out})
        socketio.sleep(2)

@app.route('/')
def index():
    try:      
        return flask.render_template('index.html')
    except ValueError:
            return str(e)
       
@socketio.on('connect')
def MBC_connect():
    print('Client Connected')
    global thread
    if not thread.isAlive():
        print("Starting Thread1")
        thread = socketio.start_background_task(RTD_Temp1)    
    global thread2
    if not thread2.isAlive():
        print("Starting Thread2")
        thread2 = socketio.start_background_task(RTD_Temp2)

@socketio.on('disconnect')
def MBC_disconnect():
    print('Client Disconnected')
    
@socketio.on('message')
def handleMessage(msg):
    print('Message: ' +msg)
    #send(msg, broadcast=True)
    
@socketio.on('sensor_change1')
def change_sensor1(index):
    print("Smoker sensor changed to: ", index)
    
@socketio.on('sensor_change2')
def change_sensor2(index):
    print("Meat sensor changed to: ", index)
    
 
if __name__ == '__main__':
    app.debug=True
    socketio.run(app, host='192.168.0.31', port=5000)