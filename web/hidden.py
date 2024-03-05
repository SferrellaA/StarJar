from random import choice, randint
from string import ascii_letters, digits

def gen_hidden():
    global hidden
    hidden = ''.join(choice(ascii_letters + digits) for _ in range(randint(10,20)))
    @app.get(f'/{hidden}')
    def victory():
        return f'<strong><p>VICTORY!</p></strong>', 233

def get_hidden():
    global hidden
    return hidden

# TODO - add a way for the player to enter initials and display a time score