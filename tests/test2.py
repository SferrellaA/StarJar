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
def flood(color):
    h, s, v = color
    for led in range(strip):
        print(led)
        plasma.set_hsv(led, h, s, v)
        
def dot(color):
    flood(blank)
    flood(color)
    sleep(0.3)
    flood(blank)

def dash(color):
    flood(blank)
    flood(color)
    sleep(0.7)
    flood(blank)
    
def blank():
    flood(blank)
    sleep(0.5)
    
def tap(color, letter):
    #flood(blank)
    for l in MORSE_CODE_DICT[letter]:
        if l == '.':
            dot(blue)
        else:
            dash(yellow)
        blank()

while True:
    flood(yellow)
    sleep(2)
    for letter in "WIFI":
        tap(blue, letter)