#!/usr/bin/python3

import RPi.GPIO as GPIO
import time

from modules.app_config import socketio


class hardwareAPI:

    def __init__(self):
        self.output1 = 26
        self.output2 = 20
        self.output3 = 21
        self.outputs = [self.output1, self.output2, self.output3]
        self.fan_states = { 0: "OFF", 1: "OFF", 2: "OFF"}

        #GPIO.setmode(GPIO.BOARD)
        GPIO.setmode(GPIO.BCM)
        for i in self.outputs:
            GPIO.setup(i, GPIO.OUT)

    def set_fan_states(self, fan_states_in):
        self.fan_states = fan_states_in

    def send_fan_states(self):
        socketio.emit("fan_states", self.fan_states)
        print("Sendng fan_states: ", self.fan_states)

    def fan_index_change(self, fan_indexes_in):
        fan_indexes = fan_indexes_in
        filename = "./config.txt"
        with open(filename, 'r') as f:
            cur_line = 0
            cfile = f.readlines()
            for line in cfile:
                cur_line +=1
                if "Fan_Indexes" in line:
                    cfile[cur_line] = str(fan_indexes) + '\n'
        with open(filename, 'w') as f:
            for i in range(0,len(cfile)):
                f.write(str(cfile[i]))         
        socketio.emit('fan_indexes', fan_indexes)
        print("Fan_Indexes Received from Client & Broadcasted: %s" % fan_indexes)
    
    def toggle_fan_state(self, fanID):
        if self.fan_states[int(fanID)] == "OFF":
            self.fan_states[int(fanID)] = "ON"
        else:
            self.fan_states[int(fanID)] = "OFF"
        x = [0,1,2]
        for y in x:
            if self.fan_states[y] == "ON":
                GPIO.output(self.outputs[y], GPIO.HIGH)
            else: 
                GPIO.output(self.outputs[y], GPIO.LOW)
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