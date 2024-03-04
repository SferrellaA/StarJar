# Generate victory code
from scripts.hidden import gen_hidden
gen_hidden()

# Handle routing
import scripts.routes

# Handle robots.txt
from bottle import route
@route('/robots.txt')
def brython():
    return static_file('robots.txt', '.')

# Actually run the server
from bottle import run
run(host='localhost', port=8080, debug=True)