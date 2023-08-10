#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("Starting MoonBrewCo...")

from pprint import pprint
import eventlet
eventlet.monkey_patch()

import modules
from modules.app_config import app, socketio, cache

def initializer():
    for i in cache["INIT"]:
        kwargs = {}
        for k, v in i.items():
            if k == "function":
                function = i[k]
            elif k == 'l_type':
                pass
            else:
                kwargs[k] = v      
        if i['l_type'] == 'active':
            f = i['function']          
            f(**kwargs)
        else:  
            thread = socketio.start_background_task(function, **kwargs)

print("Starting Background Tasks...")
initializer()

print("Full Compiled Cache...")
pprint(cache)

print("Startup Complete")

# app.debug=False #setting to True will break this code! 
socketio.run(app, host='192.168.0.31', port=5000, debug=False) #certfile='./certs/server.crt', keyfile='./certs/server.key', server_side=True)
