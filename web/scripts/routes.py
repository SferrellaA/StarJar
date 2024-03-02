from bottle import route, static_file
from os import path

interpreter = open('brython.js').read()
@route('/brython.js')
def brython():
    return interpreter

template_html = open('template.html').read()

def enscript(script):
    return f'<script type="text/python" src="/get/script/{script}"></script>'

@route('/')
def main():
    #content  = '''\
    #<script type="text/python>
    #{index}
    #</script>'
    #'''.format(index=open(path.join('scripts', 'index.py')).read())
    content = '<script type="text/python">\n{index}\n</script>\n'
    content = content.format(index=open(path.join('scripts', 'index.py')).read())
    content += enscript("css.py")
    return template_html.format(body=content)

@route('/images/<figure>')
def images(figure):
    return static_file(figure, root="images")

@route('/scripts/<script>')
def get_script(script):
    if path.exists(script):
        return open(script).read()
    return "404"
