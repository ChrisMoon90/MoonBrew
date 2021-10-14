#!/usr/bin/python3
import time
from modules.app_config import socketio


class timerAPI:

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