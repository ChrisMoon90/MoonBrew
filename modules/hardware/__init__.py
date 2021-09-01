#!/usr/bin/python3

import RPi.GPIO as GPIO
import time


class hardwareAPI:

    def __init__(self):
        self.output1 = 26
        self.output2 = 20
        self.output3 = 21
        self.outputs = [self.output1, self.output2, self.output3]

        #GPIO.setmode(GPIO.BOARD)
        GPIO.setmode(GPIO.BCM)

        for i in self.outputs:
            GPIO.setup(i, GPIO.OUT)
            #GPIO.setup(switch, GPIO.IN)

    #def toggle_fan():

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