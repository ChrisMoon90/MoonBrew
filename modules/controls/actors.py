print('Loading Actors module...')

import RPi.GPIO as GPIO
import time

from modules.app_config import cache, socketio

class ActorAPI():
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
        ActorAPI.outputs = [output1, output2, output3]

    def update_actors(self):
        for key, val in cache['ACTORS'].items():
            if val['state'] == True:
                GPIO.output(ActorAPI.outputs[key], GPIO.HIGH)
            else: 
                GPIO.output(ActorAPI.outputs[key], GPIO.LOW)
            socketio.emit('cache', cache)
        print('Actor States Updated: ', cache['ACTORS'])
        
    def cleanup():
        GPIO.cleanup()


#FOR DEVELOPMENT PURPOSES
if __name__ == '__main__': 
    a = ActorAPI()
    for f in a.outputs:
        print('Starting new fan: pin ', f)
        GPIO.output(f, GPIO.HIGH)
        time.sleep(5)
        GPIO.output(f, GPIO.LOW)
        time.sleep(1)

    a.cleanup()