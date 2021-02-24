from flask import Blueprint

react = Blueprint('react', __name__, template_folder='templates', static_folder='static')

@react.route('/')
def index():
    print("returning blueprint")
    return react.send_static_file("index.html")

