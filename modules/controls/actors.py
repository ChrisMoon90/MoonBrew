print('Loading Actors module...')

import RPi.GPIO as GPIO
import time

from modules.app_config import cache, socketio

class ActorAPI():

    outputs = [26, 20, 21]
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    for i in outputs:
        GPIO.setup(i, GPIO.OUT)
    for x in range(3):
        cache['ACTORS'][x]['state'] = False
        cache['ACTORS'][x]['dev_name'] = "Actor " + str(x + 1)

    # def __init__(self, a_num, output):
    #     self.a_num = a_num
    #     self.output = output
    #     self.state = False

    def update_actors():
        for k, v in cache['ACTORS'].items():
            if v['state'] == True:
                GPIO.output(ActorAPI.outputs[k], GPIO.HIGH)
            else: 
                GPIO.output(ActorAPI.outputs[k], GPIO.LOW)
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