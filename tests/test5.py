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
import colors
from time import sleep

# Helper Functions
def tap(strip, color):
    h, s, v = color
    for led in range(50): #is there a way to get the length?
        strip.set_hsv(led, h, s, v)

def moorse(strip, phrase, colorDot, colorDash):
    for letter in phrase:
        print(letter, end=" ")
        for l in MORSE_CODE_DICT[letter]:
            print(l, end="")
            if l == '.':
                tap(strip, colorDot)
                sleep(1.0)
            else: #dash
                tap(strip, colorDash)
                sleep(2.0)
            tap(strip, colors.blank)
            sleep(1.0)
        print()
        sleep(1.0)
    print()


# Set up the Plasma2040
from plasma import plasma_stick
from plasma import WS2812, COLOR_ORDER_RGB
strip = WS2812(50, 0, 0, plasma_stick.DAT, color_order=COLOR_ORDER_RGB)
strip.start()

while True:
    for word in "33COS WIFI".split():
        moorse(strip, word, colors.blue, colors.yellow)
        sleep(3.3)