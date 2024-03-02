from bottle import route, run, static_file
from os import path

interpreter = open(path.join('brython', 'brython.js')).read()
@route('/brython.js')
def brython():
    return interpreter

template = open('template.html').read()
def build_template(*args):
    content = ""
    for arg in args:
        content += f'<script type="text/python" src="{arg}"></script>'
    return template.format(content=content)

@route('/')
def index():
    return build_template('/brython/index.py', '/brython/css.py')

@route('/index.html')
def index_html():
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