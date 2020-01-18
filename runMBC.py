#!/usr/bin/env python

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

def randomNumberGenerator():
    print("Making random numbers")
    while not thread_stop_event.isSet():
        number = round(random()*10, 1)
        print(number)
        socketio.emit('newnumber', {'number': number}, namespace='/test')
        socketio.sleep(2)

def RTD_Temp():
    print("Starting RTD Temp Process")
    while not thread_stop_event.isSet():
        temp = sensors.run_Temp()
        temp1 = temp, " °F"
        print(temp1)
        socketio.emit('newtemp', {'temp': temp1}, namespace='/test2')
        socketio.sleep(2)


@app.route('/')
def index():
    try:      
        return flask.render_template('index.html')
    except ValueError:
            return str(e)

@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    print('Client connected')   
    if not thread.isAlive():
        print("Starting Thread1")
        thread = socketio.start_background_task(randomNumberGenerator)

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')
    
    
@socketio.on('connect', namespace='/test2')
def test_connect2():
    global thread2
    if not thread2.isAlive():
        print("Starting Thread2")
        thread2 = socketio.start_background_task(RTD_Temp)

@socketio.on('disconnect', namespace='/test2')
def test_disconnect2():
    print('Client disconnected')
    
@socketio.on('message')
def handleMessage(msg):
    print('Message: ' +msg)
    #send(msg, broadcast=True)

 
if __name__ == '__main__':
    app.debug=True
    socketio.run(app, host='192.168.0.30', port=5001)
    