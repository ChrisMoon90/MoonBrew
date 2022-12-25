#!/usr/bin/python3

from modules.app_config import socketio


class hysteresisAPI:

    def __init__(self, cache, ti2c, hw):
        self.isRunning = False
        self.tempAPI = ti2c
        self.fanAPI = hw
        self.tar_temp = cache['system']['tar_temp']
        self.temp_tol = cache['system']['temp_tol']
        
    def fetch_tar_temp(self):
        socketio.emit("TarTemp", self.tar_temp)
        print("Sent Target Temp: ", self.tar_temp)

    def set_tar_temp(self, tar_temp):
        self.tar_temp = tar_temp
        print("Target Temp Updated: ", self.tar_temp)

    def fetch_temp_tol(self):
        socketio.emit("TempTol", self.temp_tol)
        print("Sent Temp Tol: ", self.temp_tol)

    def set_temp_tol(self, temp_tol):
        self.temp_tol = temp_tol
        print("Temp Tol Updated: ", self.temp_tol)

    def update_temp_tol(self, new_temp_tol):
        self.temp_tol = new_temp_tol

    def send_auto_state(self):
        socketio.emit('auto_state', self.isRunning)
        print("AutoState Sent: ", self.isRunning)

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
            if self.cur_temp < self.tar_temp - self.temp_tol:
                if self.cur_fan_state == "OFF":
                    self.fanAPI.toggle_fan_state(self.active_fan,"ON") 
            elif self.cur_temp > self.tar_temp + self.temp_tol:
                if self.cur_fan_state == "ON":
                    self.fanAPI.toggle_fan_state(self.active_fan,"OFF") 
            socketio.sleep(sleep)
        self.fanAPI.toggle_fan_state(self.active_fan,"OFF")
        print("Hysteresis Thread Terminated & Powered Off")