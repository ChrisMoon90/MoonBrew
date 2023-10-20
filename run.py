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

import modules
from modules.app_config import app, socketio, cache

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

web.run_app(run_init(), host = '192.168.0.31', port = 5000)