import scripts.routes
import scripts.hidden
import scripts.get

from bottle import run
run(host='localhost', port=8080, debug=True)

