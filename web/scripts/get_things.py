from bottle import route

@route('/get/<kind>/<file>')
def get_thing(kind, file):
    return f'<strong>{kind}</strong><br>{file}'
    if path.exists(script):
        return open(script).read()
