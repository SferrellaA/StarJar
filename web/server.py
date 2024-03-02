from bottle import route, run, static_file
from os import path

interpreter = open('brython.js').read()
@route('/brython.js')
def brython():
    return interpreter

template = open('template.html').read()
@route('/')
def index():
    return template.format(content=open('index.py').read())

@route('/images/<figure>')
def images(figure):
    return static_file(figure, root="images")

@route('/<script>')
def get_script(script):
    if path.exists(script):
        return open(script).read()
    return "404"

run(host='localhost', port=8080, debug=True)