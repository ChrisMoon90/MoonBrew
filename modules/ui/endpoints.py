print('Loading UI module...')

import os
from datetime import datetime
from aiohttp import web
from modules.app_config import app


async def index(request):
    print('Serving the client-side application...')
    with open('./modules/ui/static/index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')

async def send_system_data(request):
    print('System data requested')
    path = "./logs/system.txt"
    if os.path.isfile(path) == True:
        with open(path, "r") as file:
            file.seek(0)
            return web.Response(text=file.read())
    else:
        print('Send system data Error: no file exists') 
 
async def send_sensor_data(request):
    print('FIX: Sensor csv data requested', datetime.now())
    path = "./logs/sensors.csv"
    if os.path.isfile(path) == True:
        with open(path, "r") as file:
            file.seek(0)
            return web.Response(text=file.read())
    else:
        print('Send sensor data Error: no file exists') 

async def redirect(request):
    raise web.HTTPFound('/')
    
app.add_routes([web.get('/', index),
                web.get('/chart', index),
                web.get('/settings', index),
                web.get('/system', index),
                web.get('/diagnostics', index),
                web.get('/api/sensors', send_sensor_data),
                web.get('/api/system', send_system_data),
                web.get('/static', redirect)])

app.router.add_static('/', 'modules/ui/static/')