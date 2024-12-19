#!/home/chrism/MoonBrew/MBC-venv/bin/python3
# -*- coding: utf-8 -*-

print("Starting MoonBrewCo...")

from modules.sys_log import sys_log
sys_log('-----------------------------------------------')
sys_log('Starting MoonBrew...')

import time
from aiohttp import web
from pprint import pprint
import socket

import modules
from modules.app_config import app, socketio, cache #, ssl_context

async def initializer():
    for i in cache["INIT"]:
        kwargs = {}
        for k, v in i.items():
            if k == "function":
                f = i[k]
            else:
                kwargs[k] = v      
        try:
            socketio.start_background_task(f, **kwargs)
        except:
            print('Error on: ', f)
    await socketio.sleep(1)
    sys_log('Finished Startup')

async def run_init():
    await initializer()
    print("Full Compiled Cache...")
    pprint(cache)
    print("Startup Complete")
    return app

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1)) # doesn't even have to be reachable
        IP = s.getsockname()[0]
    except:
        IP = '192.168.0.30'
    finally:
        s.close()
    return IP

web.run_app(run_init(), host = get_ip(), port = 5000) #, ssl_context = ssl_context)