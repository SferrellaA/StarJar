# Imports
from plasma import plasma_stick
from plasma import WS2812, COLOR_ORDER_RGB
from time import sleep
from rgb_to_hsv import rgb_to_hsv

# Informations
MORSE_CODE_DICT = { 'A':'.-', 'B':'-...',
                    'C':'-.-.', 'D':'-..', 'E':'.',
                    'F':'..-.', 'G':'--.', 'H':'....',
                    'I':'..', 'J':'.---', 'K':'-.-',
                    'L':'.-..', 'M':'--', 'N':'-.',
                    'O':'---', 'P':'.--.', 'Q':'--.-',
                    'R':'.-.', 'S':'...', 'T':'-',
                    'U':'..-', 'V':'...-', 'W':'.--',
                    'X':'-..-', 'Y':'-.--', 'Z':'--..',
                    '1':'.----', '2':'..---', '3':'...--',
                    '4':'....-', '5':'.....', '6':'-....',
                    '7':'--...', '8':'---..', '9':'----.',
                    '0':'-----', ', ':'--..--', '.':'.-.-.-',
                    '?':'..--..', '/':'-..-.', '-':'-....-',
                    '(':'-.--.', ')':'-.--.-'}
blank = rgb_to_hsv(0, 0, 0)
blue = rgb_to_hsv(1, 22, 137)
yellow = rgb_to_hsv(246, 209, 6)

# Set up the Plasma2040
strip = 50
plasma = WS2812(strip, 0, 0, plasma_stick.DAT, color_order=COLOR_ORDER_RGB)
plasma.start()

# Helper Functions
def flash(color):
    h, s, v = color
    for led in range(strip):
        plasma.set_hsv(led, h, s, v)

def pause(length):
    flash(blank)
    sleep(length)

def tap(letter, color):
    print(letter, end=" ")
    for l in MORSE_CODE_DICT[letter]:
        flash(color)
        print(l, end="")
        if l == '.':
            sleep(1.0)
        else: #dash
            sleep(2.0)
        pause(0.5)
    print()

def moorse(phrase, colors):
    c = 0
    for letter in phrase:
        tap(letter, colors[c])
        c += 1
        if c == len(colors):
            c = 0
    pause(1.0)

while True:
    moorse("WIFI", [blue, yellow])
    pause(3.3)
    moorse("33COS", [yellow, blue])
    pause(3.3)