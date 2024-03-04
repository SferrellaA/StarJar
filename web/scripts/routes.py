from bottle import route, static_file
from os import path

'''
interpreter = open('brython.js').read()
@route('/brython.js')
def brython():
    return interpreter
'''

@route('/brython.js')
def brython():
    return static_file('brython.js', '.')

@route('/brython_stdlib.js')
def brython():
    return static_file('brython_stdlib.js', '.')


template_html = open('template.html').read()

def enscript(script):
    return f'<script type="text/python" src="/get/scripts/{script}"></script>'

@route('/')
def main():
    content = '<script type="text/python">\n{index}\n</script>'
    content = content.format(index=open(path.join('scripts', 'index.py')).read())
    content += f'\n{enscript("css.py")}\n'
    return template_html.format(body=content)

# scripts and images
import scripts.get
'''
@route('/images/<figure>')
def images(figure):
    return static_file(figure, root="images")

@route('/scripts/<script>')
def get_script(script):
    if path.exists(script):
        return open(script).read()
    return "404"
'''

import scripts.hidden
