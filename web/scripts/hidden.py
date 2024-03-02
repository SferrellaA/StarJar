from bottle import route
from random import choice, randint
from string import ascii_letters, digits

hidden = ''.join(choice(ascii_letters + digits) for _ in range(randint(10,20)))
print(hidden)
@route(f'/{hidden}')
def victory():
    return f'<strong>{hidden}</strong>'

# TODO - add a way for the player to enter initials and display a time score