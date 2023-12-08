print('Loading Actors module...')

import RPi.GPIO as GPIO
import time

from modules.app_config import cache, socketio
from modules.sys_log import sys_log

class ActorAPI():

    outputs = [26, 20, 21]
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    for i in outputs:
        GPIO.setup(i, GPIO.OUT)
    for x in range(3):
        cache['ACTORS'][x]['state'] = False
        cache['ACTORS'][x]['dev_name'] = "Actor " + str(x + 1)

    async def update_actors():
        msg = {}
        for k, v in cache['ACTORS'].items():
            msg[k] = v['state']
            if v['state'] == True:
                GPIO.output(ActorAPI.outputs[k], GPIO.HIGH)
            else: 
                GPIO.output(ActorAPI.outputs[k], GPIO.LOW)
        print(msg)
        sys_log('Actor states updated: ' + str(msg))
        
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