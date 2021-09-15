#!/usr/bin/python3

from modules.app_config import socketio


class hysteresisAPI:

    def __init__(self, a, c):
        self.isRunning = False
        self.tempAPI = a
        self.fanAPI = c
        self.set_temp = 76.5
        self.temp_tol = 1

    def update_set_temp(self, new_set_temp):
        self.set_temp = new_set_temp

    def update_temp_tol(self, new_temp_tol):
        self.temp_tol = new_temp_tol

    def send_auto_state(self):
        socketio.emit('auto_state', self.isRunning)

    def toggle_auto_state(self):
        self.isRunning = not self.isRunning
        if self.isRunning == True:
            thread3 = socketio.start_background_task(target=self.hysteresis, sleep = 2)
        else:
            print("Stopping Hysteresis Thread") 
        socketio.emit('auto_state', self.isRunning)

    def hysteresis(self, sleep):
        print("Starting Hysteresis Thread")
        while self.isRunning:
            self.active_sensor = self.tempAPI.temp_indexes['s0']
            self.cur_temp = self.tempAPI.temps[self.active_sensor]
            self.active_fan = self.fanAPI.fan_indexes['f0']
            self.cur_fan_state = self.fanAPI.fan_states[self.active_fan]
            if self.cur_temp < self.set_temp - self.temp_tol:
                if self.cur_fan_state == "OFF":
                    self.fanAPI.toggle_fan_state(self.active_fan,"ON") 
            elif self.cur_temp > self.set_temp + self.temp_tol:
                if self.cur_fan_state == "ON":
                    self.fanAPI.toggle_fan_state(self.active_fan,"OFF") 
            socketio.sleep(sleep)
        self.fanAPI.toggle_fan_state(self.active_fan,"OFF")
        print("Hysteresis Thread Terminated & Powered Off")