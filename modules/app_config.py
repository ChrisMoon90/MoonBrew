import flask
from flask_socketio import SocketIO
import os
from modules.ui.endpoints import react

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins='*')

#app.add_url_rule('/favicon.ico',redirect_to=url_for('static', filename='favicon.ico'))
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://localhost:5432/flask_todo'
#db = SQLAlchemy(app)

app.register_blueprint(react, url_prefix='/ui')
#print(app.url_map)

@app.route('/')
def index0():
    try:      
        return redirect('/ui')
    except ValueError:
            return str(e)


def get_config_indexes(): 
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
                    fan_indexes_raw = cfile[cur_line]        
            temp_indexes = eval(temp_indexes_raw)
            fan_indexes = eval(fan_indexes_raw)
    else:
        print("Index file does not exist. Config file will be created.")
        temp_indexes = {'s0':0, 's1':1, 's2':2}
        fan_indexes = {'f0':0, 'f1':1, 'f2':2}
        with open(filename, 'w') as f:
            f.write("Temp_Indexes\n")
            f.write(str(temp_indexes) + "\n\n")
            f.write("Fan_Indexes\n")
            f.write(str(fan_indexes))
    indexes = [temp_indexes, fan_indexes]
    return indexes