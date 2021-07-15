from flask import Blueprint
import os

cwd = os.getcwd()
print(cwd)
dwd = cwd + '/build'
print(dwd)

react = Blueprint('react', __name__, template_folder='templates', static_folder = 'build/static', static_url_path = 'build/static')

@react.route('/')
def index():
    print("returning blueprint")
    return react.send_static_file("index.html")

path_test = react.root_path
print("Blueprint path = " + path_test)
