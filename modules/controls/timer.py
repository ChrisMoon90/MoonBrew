print('Loading Timer module...')

import time
from datetime import datetime
from modules.app_config import socketio

class TimerAPI:

    start_time = 0

    def set_start_time():
        TimerAPI.start_time = datetime.now()
        # TimerAPI.send_start_time()

    def reset_timer():
        TimerAPI.start_time = 0
        # TimerAPI.send_start_time()

    # def update_to_cache():
    #     cache['']
    
    # async def send_start_time():
    #     await socketio.emit("start_time", str(TimerAPI.start_time))
    #     print("Sending start time: ", str(TimerAPI.start_time))


# # TIMER FUNCTIONS ############################
# @socketio.on('fetch_timer')
# async def send_start_time(sid):
#     await TimerAPI.send_start_time()

# @socketio.on('start_timer')
# async def start_timer(sid):
#     TimerAPI.start_timer()

# @socketio.on('reset_timer')
# async def reset_timer(sid):
#     TimerAPI.reset_timer()