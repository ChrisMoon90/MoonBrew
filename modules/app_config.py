import flask
from flask_socketio import SocketIO
import os
import pprint
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
        "init": [],
        "sensors":{},
        "hardware":{
            0:{},
            1:{},
            2:{}
            },
        "vessels":{},
        "system": {
            "auto_state": "OFF"
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
        mode = 'brew'
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
    vessels = {'boil_kettle': bk_indexes, 'mash_tun': mt_indexes, 'hot_liquor_tank': hlt_indexes, 'fermenter': ferm_indexes, 'smoker': smkr_indexes}
    for key in vessels:
        cache['vessels'][key] = vessels[key]
    cache['system']['mode'] = mode
    cache['system']['tar_temp'] = tar_temp
    cache['system']['temp_tol'] = temp_tol
    #pprint.pprint(cache)

get_config_params()