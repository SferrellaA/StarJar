import scripts.routes
import scripts.hidden
import scripts.get_things

from bottle import run
run(host='localhost', port=8080, debug=True)

