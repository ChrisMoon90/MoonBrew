print('Loading Config module...')

from aiohttp import web
import aiohttp_cors
import socketio as sio
import os


socketio = sio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
app = web.Application()
socketio.attach(app)


# routes = web.RouteTableDef()

# @routes.get('/')
async def index(request):
    """Serve the client-side application."""
    with open('index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')


# cors = aiohttp_cors.setup(app)
# resource = cors.add(app.router.add_resource("/"))
# route = app.router.add_post("/", index)
# cors.add(
#     route,
#     {
#         "*": aiohttp_cors.ResourceOptions(
#             allow_credentials=True,
#             expose_headers=("X-Custom-Server-Header",),
#             allow_methods=["POST", "PUT"],
#             allow_headers=("X-Requested-With", "Content-Type"),
#         )
#     },
# )

# app.router.add_post("/", index)
# cors = aiohttp_cors.setup(app, defaults={
#    "*": aiohttp_cors.ResourceOptions(
#         allow_credentials=True,
#         expose_headers="*",
#         allow_headers="*"
#     )
#   })

# for route in list(app.router.routes()):
#     cors.add(route)
    
# route = cors.add(
#     resource.add_route("GET", index), {
#         "*": aiohttp_cors.ResourceOptions(allow_credentials=True)
#     })

# app.add_routes([route])

# app.router.add_static('/modules/ui/build/static', 'modules/ui/build/static')

# @app.route('/data')
# @routes.get('/data')
def send_csv_data():
    filename = "./logs/Temps.csv"
    with open(filename, "r") as file:
        file.seek(0)
        csv_data = file.read()
    return csv_data


# SET UP CACHE & CONFIG PARAMETERS ###################
global cache
cache = {           
        "INIT": [],
        "SENSORS":{},
        "ACTORS":{
            0:{},
            1:{},
            2:{}
            },
        "VESSELS":{
            'Boil_Kettle': {},
            'Mash_Tun': {},
            'Hot_Liquor_Tank': {},
            'Fermenter': {},
            'Smoker': {}
        },
        "SYSTEM": { 
            'Dynamic': {
                'log_state': False,
                'timer_start': None
                },
            'AutoStates': {
                'Boil_Kettle': False,
                'Mash_Tun': False,
                'Hot_Liquor_Tank': False,
                'Fermenter': False,
                'Smoker': False
            }
        }
    }

def get_config_params(): 
    filename = "./config.txt"
    settings = ['Boil_Kettle', 'Mash_Tun', 'Hot_Liquor_Tank', 'Fermenter', 'Smoker']
    if os.path.exists(filename):
        pass
    else:
        print("Index file does not exist. Config file will be created.")
        with open(filename, 'w') as f:
            f.write("SYSTEM\n")
            f.write("'Static': {'Mode': 'Brew', 'log_rate': 1}\n\n")
            a = {'Actors': {},
                'Sensors': {},
                'Params': {'tar_temp': 200, 'temp_tol': 2}}
            for i in settings:
                f.write(str(i) + '\n')
                for p in a:
                    f.write("'" + str(p) + "': " + str(a[p]) + '\n')
                f.write('\n')
    with open(filename, 'r+') as f:  # ADD TO CACHE
        x = 0
        cfile = f.readlines()          
        for line in cfile:
            for i in settings:
                if 'SYSTEM' in line:
                    static = eval('{' + str(cfile[x + 1]).rstrip("\n") + '}')
                    cache['SYSTEM']['Static'] = static['Static']
                    break
                elif i in line:
                    actors = cfile[x + 1].rstrip("\n")
                    sensors = cfile[x + 2].rstrip("\n")
                    params = cfile[x + 3].rstrip("\n")
                    set = eval('{' + actors + ', ' + sensors + ', ' + params + '}')
                    cache['VESSELS'][i] = set
            x += 1

async def update_config(dir, *args):
    filename = "./config.txt"
    with open(filename, 'r') as f:
        cur_line = 0
        cfile = f.readlines()
        for line in cfile:
            cur_line +=1           
            if dir == 'SYSTEM':
                if dir in line:
                    dict = args[0]
                    cfile[cur_line] = "'Static': " + str(dict['Static']) + '\n'
            if dir == "VESSELS":
                if args[0] in line:
                    dict = args[1]
                    cfile[cur_line] = "'Actors': " + str(dict['Actors']) + '\n'
                    cfile[cur_line+1] = "'Sensors': " + str(dict['Sensors']) + '\n'
                    cfile[cur_line+2] = "'Params': " + str(dict['Params']) + '\n'
    with open(filename, 'w') as f:
        for i in range(0,len(cfile)):
            f.write(str(cfile[i]))

get_config_params()