import flask
from flask import redirect
from flask_socketio import SocketIO, emit

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

import modules.ui
from modules.sensors import *
from modules.ui.endpoints import react

#app.add_url_rule('/favicon.ico',redirect_to=url_for('static', filename='favicon.ico'))
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://localhost:5432/flask_todo'
#db = SQLAlchemy(app)
  
indexes = {'s0':0, 's1':1, 's2':2}
print(indexes)
@socketio.on('connect')
def MBC_connect():
    print('Client Connected')
    socketio.emit('connected',  {'connected': 'Connection Request Accepted'})
    socketio.emit('indexes', indexes)
   
@socketio.on('disconnect')
def MBC_disconnect():
    print('Client Disconnected')

@socketio.on('index_change')
def index_change(indexes_in):
    global indexes
    indexes = indexes_in
    socketio.emit('indexes', indexes)
    print("Indexes Received from Client & Broadcasted: %s" % indexes)
    
@app.route('/')
def index0():
    try:      
        return redirect('/ui')
    except ValueError:
            return str(e)


app.register_blueprint(react, url_prefix='/ui')
print("Blueprints Registered")
print(app.url_map)


#if __name__ == '__main__':     
print("Starting Threads")
thread = socketio.start_background_task(RTD_Temp)
