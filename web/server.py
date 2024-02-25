from bottle import route, run, static_file
from os import path

@route('/')
def index():
    return open("index.html").read()

@route('/images/<figure>')
def images(figure):
    return static_file(figure, root="images")

@route('/brython/<script>')
def get_script(script):
    full_path = path.join("brython", script)
    if path.exists(full_path):
        return open(full_path).read()
    return "404"

run(host='localhost', port=8080, debug=True)