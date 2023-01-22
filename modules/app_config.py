import flask
from flask_socketio import SocketIO
import os
import pprint
import json

from modules.ui.endpoints import react


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
        "HARDWARE":{
            0:{},
            1:{},
            2:{}
            },
        "VESSELS":{},
        "SYSTEM": {
            "Auto_State": "OFF"
        }
    }

def get_config_params(): 
    filename = "./config.txt"
    if os.path.exists(filename):
        with open(filename, 'r+') as f:
            cur_line = 0
            cfile = f.readlines()
            for x in cfile:
                cur_line += 1
                if "Mode" in x:
                    mode = cfile[cur_line].rstrip("\n")
                if "Boil_Kettle" in x:
                    bk_indexes = eval(cfile[cur_line].rstrip("\n"))
                if "Mash_Tun" in x:
                    mt_indexes = eval(cfile[cur_line].rstrip("\n"))
                if "Hot_Liquor_Tank" in x:
                    hlt_indexes = eval(cfile[cur_line].rstrip("\n"))
                if "Fermenter" in x:
                    ferm_indexes = eval(cfile[cur_line].rstrip("\n"))
                if "Smoker" in x:
                    smkr_indexes = eval(cfile[cur_line].rstrip("\n"))
                if "Target_Temp" in x:
                    tar_temp = eval(cfile[cur_line].rstrip("\n"))
                if "Temp_Tollerance" in x:
                    temp_tol = eval(cfile[cur_line].rstrip("\n"))
    else:
        print("Index file does not exist. Config file will be created.")
        mode = 'Brew'
        bk_indexes = {'s0':0, 'h0':0, 'h1':1}
        mt_indexes = {'s0':0, 'h0':0}
        hlt_indexes = {'s0':0, 'h0':0, 'h1':1}
        ferm_indexes = {'s0':0, 's1':1,'s2':2, 'h0':0, 'h1':1}
        smkr_indexes = {'s0':0, 's1':1, 'h0':0, 'h1':1}
        tar_temp = 200
        temp_tol = 5
        with open(filename, 'w') as f:
            f.write("Mode\n" + str(mode) + "\n\n")
            f.write("Boil_Kettle\n" + str(bk_indexes) + "\n\n")
            f.write("Mash_Tun\n" + str(mt_indexes) + "\n\n")
            f.write("Hot_Liquor_Tank\n" + str(hlt_indexes) + "\n\n")
            f.write("Fermenter\n" + str(ferm_indexes) + "\n\n")
            f.write("Smoker\n" + str(smkr_indexes) + "\n\n")
            f.write("Target_Temp\n" + str(tar_temp) + "\n\n")
            f.write("Temp_Tollerance\n" + str(temp_tol) + "\n\n")
    # ADD TO CACHE
    vessels = {'Boil_Kettle': bk_indexes, 'Mash_Tun': mt_indexes, 'Hot_Liquor_Tank': hlt_indexes, 'Fermenter': ferm_indexes, 'Smoker': smkr_indexes}
    for key in vessels:
        cache['VESSELS'][key] = vessels[key]
    cache['SYSTEM']['Mode'] = mode
    cache['SYSTEM']['Tar_Temp'] = tar_temp
    cache['SYSTEM']['Temp_Tol'] = temp_tol
    #pprint.pprint(cache)

def update_config(loc, val):
    filename = "./config.txt"
    with open(filename, 'r') as f:
        cur_line = 0
        cfile = f.readlines()
        for line in cfile:
            cur_line +=1
            if loc in line:
                cfile[cur_line] = str(val) + '\n'
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
        self.cache_update()
        cache_emit = self.cache
        try: 
            del cache_emit['INIT']
        except:
            pass
        socketio.emit('cache', cache_emit)

    def update_param(self, type, loc, val):
        update_config(loc, val)
        self.cache[type][loc] = val
        self.send_cache()
        print('Parameter Update --> %s: %s' % (loc, val))