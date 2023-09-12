#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("Starting MoonBrewCo...")

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

web.run_app(run_init(), host = '192.168.0.31', port = 5000)