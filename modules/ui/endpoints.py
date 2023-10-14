print('Loading UI module...')

import os
from aiohttp import web
from modules.app_config import app


async def index():
    print('Serving the client-side application...')
    with open('./modules/ui/static/index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')

routes = web.RouteTableDef()

@routes.get('/')
async def get_main(request):
    return await index()

@routes.get('/chart')
async def get_chart(request):
    return await index()

@routes.get('/settings')
async def get_settings(request):
    return await index()

@routes.get('/data')
def send_csv_data(request):
    filename = "./logs/Sensors.csv"
    if os.path.isfile(filename) == True:
        with open(filename, "r") as file:
            file.seek(0)
            csv_data = file.read()
        return web.Response(text=csv_data)
    else:
        print('Send_csv_data Error: no csv file exists') 

app.router.add_static('/modules/ui/static', 'modules/ui/static')

app.add_routes(routes)