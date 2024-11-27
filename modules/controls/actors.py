print('Loading Actors module...')

import time
import gpiod

from modules.app_config import cache
from modules.sys_log import sys_log

class ActorAPI():

    outputs = [26, 20, 23, 21]
    for x in range(4):
        cache['ACTORS'][x]['state'] = False
        cache['ACTORS'][x]['dev_name'] = "Actor " + str(x + 1)
        cache['ACTORS'][x]['pin'] = outputs[x]

    async def update_actors():
        msg = {}
        for k, v in cache['ACTORS'].items():
            msg[k] = v['state']
            pin = v['pin']
            with gpiod.request_lines(
                    "/dev/gpiochip0",
                    consumer="actor_pwr",
                    config={
                        pin: gpiod.LineSettings(
                            direction=gpiod.line.Direction.OUTPUT, output_value=gpiod.line.Value.ACTIVE
                        )
                    },
                ) as request:
                    if v['state'] == True:
                        request.set_value(pin, gpiod.line.Value.ACTIVE)
                    else: 
                        request.set_value(pin, gpiod.line.Value.INACTIVE)
        sys_log('Actor states updated: ' + str(msg))
        
    # def cleanup():
    #     GPIO.cleanup()


#FOR DEVELOPMENT PURPOSES
if __name__ == '__main__': 
    a = ActorAPI()
    for f in a.outputs:
        print('Starting new fan: pin ', f)
        # GPIO.output(f, GPIO.HIGH)
        time.sleep(5)
        # GPIO.output(f, GPIO.LOW)
        time.sleep(1)
    a.cleanup()