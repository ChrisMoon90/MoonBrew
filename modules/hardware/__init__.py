#!/usr/bin/python3

import RPi.GPIO as GPIO
import time

from modules.app_config import socketio, cache


class hardwareAPI:
    def __init__(self):
        self.set_outputs()
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        for i in self.outputs:
            GPIO.setup(i, GPIO.OUT)
        for x in range(3):
            cache['ACTORS'][x]['state'] = False
            cache['ACTORS'][x]['dev_name'] = "Actor " + str(x + 1)

    def set_outputs(self):
        output1 = 26
        output2 = 20
        output3 = 21
        self.outputs = [output1, output2, output3]

    def toggle_actor_state(self, index):
        state = cache['ACTORS'][index]['state']
        if state == True:
            GPIO.output(self.outputs[index], GPIO.HIGH)
        else: 
            GPIO.output(self.outputs[index], GPIO.LOW)
        print('Actor State Updated: ', cache['ACTORS'])

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