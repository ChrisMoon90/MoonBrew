#!/usr/bin/python3

import RPi.GPIO as GPIO
import time

from modules.app_config import *


class fanAPI:

    def __init__(self, c):
        self.set_outputs()
        self.get_fan_indexes()
        self.fan_states = { 0: "OFF", 1: "OFF", 2: "OFF"}
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        for i in self.outputs:
            GPIO.setup(i, GPIO.OUT)

    def set_outputs(self):
        output1 = 26
        output2 = 20
        output3 = 21
        self.outputs = [output1, output2, output3]

    def send_fan_indexes(self):
        socketio.emit('fan_indexes', self.fan_indexes)
        print("Sent fan_indexes: ", self.fan_indexes)

    def get_fan_indexes(self):
        indexes = get_config_indexes()
        self.fan_indexes = indexes[1]

    def fan_index_change(self, fan_indexes_in):
        self.fan_indexes = fan_indexes_in
        filename = "./config.txt"
        with open(filename, 'r') as f:
            cur_line = 0
            cfile = f.readlines()
            for line in cfile:
                cur_line +=1
                if "Fan_Indexes" in line:
                    cfile[cur_line] = str(self.fan_indexes) + '\n'
        with open(filename, 'w') as f:
            for i in range(0,len(cfile)):
                f.write(str(cfile[i]))    
        self.send_fan_indexes()     
        print("Fan_Indexes Received from Client & Broadcasted: %s" % self.fan_indexes)
    
    def set_fan_states(self, fan_states_in):
        self.fan_states = fan_states_in

    def send_fan_states(self):
        socketio.emit("fan_states", self.fan_states)
        print("Sent fan_states: ", self.fan_states)

    def toggle_fan_state(self, fanID, fan_state):
        self.fan_states[int(fanID)] = fan_state
        x = [0,1,2]
        for y in x:
            if self.fan_states[y] == "ON":
                GPIO.output(self.outputs[y], GPIO.HIGH)
            else: 
                GPIO.output(self.outputs[y], GPIO.LOW)
        print('fan_states updated: ', self.fan_states)
        socketio.emit('fan_states', self.fan_states)

    def cleanup():
        GPIO.cleanup()


#FOR DEVELOPMENT PURPOSES
if __name__ == '__main__': 
    a = hardwareAPI()
    for f in a.outputs:
        print('Starting new fan: pin ', f)
        GPIO.output(f, GPIO.HIGH)
        time.sleep(5)
        GPIO.output(f, GPIO.LOW)
        time.sleep(1)

    a.cleanup()