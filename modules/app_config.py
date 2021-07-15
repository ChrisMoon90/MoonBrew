import flask
from flask_socketio import SocketIO
from modules.ui.endpoints import react

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins='*')

#app.add_url_rule('/favicon.ico',redirect_to=url_for('static', filename='favicon.ico'))
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://localhost:5432/flask_todo'
#db = SQLAlchemy(app)

app.register_blueprint(react, url_prefix='/ui')
#print(app.url_map)