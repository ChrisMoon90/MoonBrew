#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("Starting MoonBrewCo...")

import time
def MBC_log(msg):
    try:
        c_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        with open('./logs/MBC_log.txt', "a") as f:
            f.write(str(c_time) + ': ' + msg + '\n')
    except Exception as e:
        print('MBC_log error: ' + e)

MBC_log('Starting MoonBrew...')

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

async def run_init():
    await initializer()
    print("Full Compiled Cache...")
    pprint(cache)
    print("Startup Complete")
    return app

MBC_log('Finished Startup')

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