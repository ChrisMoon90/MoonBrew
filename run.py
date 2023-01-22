#!/usr/bin/env python3
# -*- coding: utf-8 -*-
print("Starting MoonBrewCo...")
import eventlet
eventlet.monkey_patch()
from modules import *

print("Startup Complete")
# app.debug=False #setting to True will break this code! 
socketio.run(app, host='192.168.0.31', port=5000, debug=False) #certfile='./certs/server.crt', keyfile='./certs/server.key', server_side=True)
