import flask
from flask_socketio import SocketIO
import os
import pprint

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
            self.cache[dir][int(args[0])] = args[1]
        else:  
            args = self.convert_strings(*args)        
            if dir == 'SYSTEM':          
                self.cache[dir] = args[0]
            if dir == 'VESSELS':
                self.cache[dir][args[0]] = args[1]
        update_config(dir, *args)
        self.send_cache()
        pprint.pprint(self.cache)

    def add_remove_hardware(self, mod_type, vessel, hw_type):
        v_dict = self.cache['VESSELS'][vessel]
        count = len(v_dict[hw_type])
        if mod_type == "add":
            if hw_type == "Actors":
                print("Adding Actor to ", vessel)
                v_dict[hw_type][int(count)] = {'name': 'Actor1', 'index': 0}
            else:
                print("Adding Sensor to ", vessel)
                v_dict[hw_type][int(count)] = {'name': 'Temp', 'index': 0}
        else:
            print("Deleting " + hw_type + ' from ' + vessel)
            del v_dict[hw_type][int(count - 1)]
        self.update_cache('VESSELS', vessel, v_dict)

    def convert_strings(self, *args):
        args_out = []
        for r in args:
            if type(r) is dict:
                for x in self.dfilter(r):
                    r = x
            args_out.append(r)
        return args_out

    def dfilter(self, d):
        for key, val in d.items():
            try:
                if type(key) is int:
                    pass
                else:
                    d[int(key)] = val
                    del d[key]
            except:
                pass
            if type(val) is dict:
                yield from self.dfilter(val)
            else:
                if val == True or val == False:
                    pass
                else:
                    try:
                        d[key] = int(val)
                    except:
                        d[key] = val
        yield d