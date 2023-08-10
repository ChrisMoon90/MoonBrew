print('Loading Timer module...')

import time
from modules.app_config import socketio

class TimerAPI:

    def __init__(self):
        self.start_time= 0

    def start_timer(self):
        self.start_time = int(round(time.time() * 1000))
        self.send_start_time()

    def reset_timer(self):
        self.start_time = 0
        self.send_start_time()
    
    def send_start_time(self):
        socketio.emit("start_time", self.start_time)
        print("Sending start time: ", self.start_time)


# TIMER FUNCTIONS ############################
@socketio.on('fetch_timer')
def send_start_time():
    TimerAPI.send_start_time()

@socketio.on('start_timer')
def start_timer():
    TimerAPI.start_timer()

@socketio.on('reset_timer')
def reset_timer():
    TimerAPI.reset_timer()