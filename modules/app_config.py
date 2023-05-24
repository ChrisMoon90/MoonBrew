import flask
from flask_socketio import SocketIO
import os
import pprint
# import json

from modules.ui.endpoints import react
import pprint


# SET UP FLASK SERVER ################
app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins='*')

app.register_blueprint(react, url_prefix='/') # was '/ui'
#print(app.url_map)

@app.route('/data')
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
            '0':{},
            '1':{},
            '2':{}
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
                'timer_start': None}
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
            f.write("'Static': {'Mode': 'Brew', 'log_rate': '1'}\n\n")
            a = {'Actors': {},
                'Sensors': {},
                'Params': {'auto_state': False, 'tar_temp': 200, 'temp_tol': 2}}
            for i in settings:
                f.write(str(i) + '\n')
                for p in a:
                    f.write("'" + str(p) + "': " + str(a[p]) + '\n')
                f.write('\n')
    # ADD TO CACHE
    with open(filename, 'r+') as f:
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


def update_config(dir, *args):
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
                    print('Dict: %s' % dict)
                    cfile[cur_line] = "'Actors': " + str(dict['Actors']) + '\n'
                    cfile[cur_line+1] = "'Sensors': " + str(dict['Sensors']) + '\n'
                    cfile[cur_line+2] = "'Params': " + str(dict['Params']) + '\n'
    with open(filename, 'w') as f:
        for i in range(0,len(cfile)):
            f.write(str(cfile[i]))

get_config_params()


class CacheAPI:
    def __init__(self):
        self.cache = cache

    def cache_update(self):
        self.cache = cache

    def send_cache(self):
        cache_emit = self.cache
        try: 
            del cache_emit['INIT']
        except:
            pass
        socketio.emit('cache', cache_emit)

    def update_cache(self, dir, *args):
        if dir == "ACTORS":
            self.cache[dir][str(args[0])] = args[1]
        else:
            update_config(dir, *args)
            if dir == 'SYSTEM':          
                self.cache[dir] = args[0]
            if dir == 'VESSELS':
                self.cache[dir][args[0]] = args[1]
        self.send_cache()
        pprint.pprint(self.cache)

    def add_remove_hardware(self, mod_type, vessel, hw_type):
        v_dict = self.cache['VESSELS'][vessel]
        count = len(v_dict[hw_type])
        print(type(count))
        print(v_dict)
        if mod_type == "add":
            if hw_type == "Actors":
                print("Adding Actor")
                v_dict[hw_type][str(count)] = {'name': 'Actor1', 'index': 0}
            else:
                print("Adding Sensor")
                v_dict[hw_type][str(count)] = {'name': 'Temp', 'index': 0}
        else:
            print("Deleting " + hw_type)
            del v_dict[hw_type][str(count - 1)]
        print(v_dict)
        self.update_cache('VESSELS', vessel, v_dict)