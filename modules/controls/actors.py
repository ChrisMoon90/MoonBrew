print('Loading Actors module...')

import RPi.GPIO as GPIO
import time

from modules.app_config import cache, socketio

class ActorAPI():

    def __init__(self, a_num, output):
        self.a_num = a_num
        self.output = output
        self.state = False

    def turn_on(self):
        GPIO.output(self.output, GPIO.HIGH)
        self.state = True
        
    def turn_off(self):
        GPIO.output(self.output, GPIO.LOW)
        self.state = False
        
    def cleanup():
        GPIO.cleanup()


def update_actors():
    for k, v in cache['ACTORS'].items():
        c_name = cache['ACTORS'][k]['c_name']
        if cache['ACTORS'][k]['state'] == True:
            c_name.turn_on()
        else: 
            c_name.turn_off()
    socketio.emit('cache', cache)
    print('Actor States Updated: ', cache['ACTORS'])

outputs = [26, 20, 21]
def init():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    for i in outputs:
        GPIO.setup(i, GPIO.OUT)
    for x in range(3):
        actor = ActorAPI(x, outputs[x])
        cache['ACTORS'][x]['c_name'] = actor
        cache['ACTORS'][x]['state'] = False
        cache['ACTORS'][x]['dev_name'] = "Actor " + str(x + 1)

init()


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