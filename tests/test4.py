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
def tap(color):
    h, s, v = color
    for led in range(strip):
        plasma.set_hsv(led, h, s, v)

def moorse(phrase):
    for letter in phrase:
        print(letter, end=" ")
        for l in MORSE_CODE_DICT[letter]:
            print(l, end="")
            if l == '.':
                tap(blue)
                sleep(1.0)
            else: #dash
                tap(yellow)
                sleep(2.0)
            tap(blank)
            sleep(0.5)
        print()
        sleep(1.0)
    print()

while True:
    moorse("WIFI")
    sleep(3.3)
    moorse("33COS")
    sleep(3.3)