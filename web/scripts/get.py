from bottle import route
from os import path

@route('/get/<kind>/<file>')
def get(kind, file):
    if kind == "script":
        script = path.join('scripts', file)
        if path.exists(script):
            return open(script).read()
    return f'<strong>{kind}</strong><br>{file}'
