import scripts.routes
from bottle import run

from scripts.hidden import gen_hidden
gen_hidden()

run(host='localhost', port=8080, debug=True)