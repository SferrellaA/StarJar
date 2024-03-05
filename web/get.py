#from bottle import route, static_file, HTTPResponse
from microdot import send_file
from os import path, listdir
from random import choice
from scripts.hidden import get_hidden

@app.get('/get/<kind>/<file>')
def get_file(request, kind, file):
    if kind == "scripts":
        script = path.join('scripts', file)
        if path.exists(script):
            return open(script).read()
    if kind == "images":
        image = path.join('images', file)
        if path.exists(image):
            return static_file(file, 'images')
    return f'<strong>{kind}</strong><br>{file}'

@app.get('/get/<kind>')
def get_kind(request, kind):
    if kind == "hidden":
        return get_hidden()
    if kind == "scripts":
        return '<br>'.join(listdir(kind))
    if kind == "images":
        file = choice(listdir(kind))
        return path.join("get", kind, file)
    return f'<strong>{kind}</strong>', 433