from os import path
from microdot import send_file

def setup_routes(app):
    @app.get('/brython.js')
    def brython(request):
        return send_file('./brython.js')

    @app.get('/brython_stdlib.js')
    def brython_stdlib(request):
        return send_file('./brython_stdlib.js')

    @app.get('/robots.txt')
    def robots(request):
        return send_file('./robots.txt')

    template_html = open('template.html').read()
    @app.get('/')
    def main(request):
        content = '<script type="text/python">\n{index}\n</script>'
        content = content.format(index=open(path.join('scripts', 'index.py')).read())
        content += f'\n{enscript("css.py")}\n'
        content += f'\n<script type="text/python" src="/get/scripts/css.py"></script>\n'
        return template_html.format(body=content)
    
    import scripts.get
    import scripts.hidden

'''
# TODO - shift this into a separate 'get' file
@route('/images/<figure>')
def images(figure):
    return static_file(figure, root="images")

@route('/scripts/<script>')
def get_script(script):
    if path.exists(script):
        return open(script).read()
    return "404"
'''