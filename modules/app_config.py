import flask
from flask_socketio import SocketIO
import os
import pprint
from modules.ui.endpoints import react


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

def get_config_params(cache): 
    filename = "./config.txt"
    if os.path.exists(filename):
        with open(filename, 'r+') as f:
            cur_line = 0
            cfile = f.readlines()
            for x in cfile:
                cur_line += 1
                if "Temp_Indexes" in x:
                    temp_indexes_raw = cfile[cur_line].rstrip("\n")
                if "Fan_Indexes" in x:
                    fan_indexes_raw = cfile[cur_line].rstrip("\n")
                if "Target_Temp" in x:
                    tar_temp = cfile[cur_line].rstrip("\n")
                if "Temp_Tollerance" in x:
                    temp_tol = cfile[cur_line].rstrip("\n")
            temp_indexes = eval(temp_indexes_raw)
            fan_indexes = eval(fan_indexes_raw)
            tar_temp = eval(tar_temp)
            temp_tol = eval(temp_tol)
    else:
        print("Index file does not exist. Config file will be created.")
        temp_indexes = {'s0':0, 's1':1, 's2':2}
        fan_indexes = {'f0':0, 'f1':1, 'f2':2}
        tar_temp = 200
        temp_tol = 5
        with open(filename, 'w') as f:
            f.write("Temp_Indexes\n")
            f.write(str(temp_indexes) + "\n\n")
            f.write("Fan_Indexes\n")
            f.write(str(fan_indexes) + "\n\n")
            f.write("Target_Temp\n")
            f.write(str(tar_temp) + "\n\n")
            f.write("Temp_Tollerance\n")
            f.write(str(temp_tol) + "\n\n")
    x = 0
    for key, value in temp_indexes:
        cache['sensors'][x] = {}
        cache['sensors'][x]['index'] =  value
        x +=1
    x = 0
    for key, value in fan_indexes:
        cache['hardware'][x] = {'index': value}
        x +=1
    cache['system']['tar_temp'] = tar_temp
    cache['system']['temp_tol'] = temp_tol
    # pprint.pprint(cache)
    # indexes = [temp_indexes, fan_indexes]
    # return indexes