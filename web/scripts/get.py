from bottle import route, static_file, HTTPResponse
from os import path, listdir
from random import choice

@route('/get/<kind>/<file>')
def get_file(kind, file):
    if kind == "scripts":
        script = path.join('scripts', file)
        if path.exists(script):
            return open(script).read()
    if kind == "images":
        image = path.join('images', file)
        if path.exists(image):
            return static_file(file, 'images')
    return f'<strong>{kind}</strong><br>{file}'

@route('/get/<kind>')
def get_kind(kind):
    try:
        file = choice(listdir(kind))
        file = path.join("get", kind, file)
        return file
        #file = open(file, 'r')
        #image = file.read()
        #file.close()
        #return image
    except:
        return HTTPResponse(status=404, body=f'<strong>{kind}</strong>')

'''


folder_path = '/path/to/your/folder'
file_list = os.listdir(folder_path)

if file_list:
    random_file = random.choice(file_list)
    print(f"Randomly selected file: {random_file}")
else:
    print("The folder is empty.")
'''


'''
@route('/get/<kind>/<file>')
def get_file(kind, file):
    asset = path.join('.', kind, file)
    print(asset)
    if not path.exists(asset):
        return HTTPResponse(status=404)
    return open(asset).read() 
'''

