import colors
from time import sleep

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