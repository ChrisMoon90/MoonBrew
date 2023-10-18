print('Loading UI module...')

import os
from aiohttp import web
from modules.app_config import app


async def index(request):
    print('Serving the client-side application...')
    with open('./modules/ui/static/index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')

async def send_csv_data(request):
    filename = "./logs/Sensors.csv"
    if os.path.isfile(filename) == True:
        with open(filename, "r") as file:
            file.seek(0)
            csv_data = file.read()
        return web.Response(text=csv_data)
    else:
        print('Send_csv_data Error: no csv file exists') 

async def redirect(request):
    raise web.HTTPFound('/')
    
app.add_routes([web.get('/', index),
                web.get('/chart', index),
                web.get('/settings', index),
                web.get('/data', send_csv_data),
                web.get('/static', redirect)])

app.router.add_static('/', 'modules/ui/static/')