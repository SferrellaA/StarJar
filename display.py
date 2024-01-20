from time import sleep as block_sleep
from random import random, uniform
import uasyncio
from plasma import plasma_stick, WS2812, COLOR_ORDER_RGB

class LED_Strip:
    def __init__(self, NUM_LEDS):
        self.NUM_LEDS = NUM_LEDS
        self.strip = WS2812(NUM_LEDS, 0, 0, plasma_stick.DAT, color_order=COLOR_ORDER_RGB)
        self.strip.start()

    def flash(self, r, g, b):
        for led in range(self.NUM_LEDS): 
            self.strip.set_rgb(led, r, g, b)

    async def timed_effect(self, time, effect, *args):
        try:
            await uasyncio.wait_for(effect(*args), time)
        except uasyncio.TimeoutError:
            pass
        self.flash(0,0,0)

    def dazzle_effect(self,
           intensity, # How much dazzle? [bigger number = more dazzle]
           # Change your colours here! RGB colour picker: https://g.co/kgs/k2Egjk
           background,
           color,
           # how quickly current colour changes to target colour [1 - 255]
           fadeIn,
           fadeOut):
        # Create a list of [r, g, b] values that will hold current LED colours, for display
        current_leds = [[0] * 3 for i in range(self.NUM_LEDS)]
        # Create a list of [r, g, b] values that will hold target LED colours, to move towards
        target_leds = [[0] * 3 for i in range(self.NUM_LEDS)]
        while True:
            for i in range(self.NUM_LEDS):
                # randomly add sparkles
                if intensity > uniform(0, 1):
                    # set a target to start a sparkle
                    target_leds[i] = color
                # for any sparkles that have achieved max sparkliness, reset them to background
                if current_leds[i] == target_leds[i]:
                    target_leds[i] = background
                # nudge our current colours closer to the target colours
                for c in range(3):  # 3 times, for R, G & B channels
                    if current_leds[i][c] < target_leds[i][c]:
                        # increase current, up to a maximum of target
                        current_leds[i][c] = min(current_leds[i][c] + fadeIn, target_leds[i][c])  
                    elif current_leds[i][c] > target_leds[i][c]:
                        # reduce current, down to a minimum of target
                        current_leds[i][c] = max(current_leds[i][c] - fadeOut, target_leds[i][c])  
                # display current colours to strip
                self.strip.set_rgb(i, current_leds[i][0], current_leds[i][1], current_leds[i][2])
            await uasyncio.sleep(0.0001)

    def sparkle(self, time):
        intensity = 0.005 
        background = [50, 50, 0]
        color = [255, 255, 0]
        fadeIn = 2
        fadeOut = 2
        uasyncio.run(self.timed_effect(time, self.dazzle_effect, intensity, background, color, fadeIn, fadeOut))

    def snow(self, time):
        intensity = 0.0002
        background = [30, 50, 50]  # dim blue
        color = [240, 255, 255]  # bluish white
        fadeIn = 255  # abrupt change for a snowflake
        fadeOut = 1
        uasyncio.run(self.timed_effect(time, self.dazzle_effect, intensity, background, color, fadeIn, fadeOut))
    
    def fire(self, time):
        def fire_effect():
            while True:
                # Random red/orange hue, full saturation, random brightness
                for i in range(self.NUM_LEDS):
                    self.strip.set_hsv(i, uniform(0.0, 50 / 360), 1.0, random())
                await uasyncio.sleep(0.1)
        uasyncio.run(self.timed_effect(time, fire_effect))
    
    def rainbow(self, time):
        def rainbow_effect():
            SPEED = 20 # The SPEED that the LEDs cycle at (1 - 255)
            UPDATES = 60 # How many times the LEDs will be updated per second
            offset = 0.0
            while True:
                SPEED = min(255, max(1, SPEED))
                offset += float(SPEED) / 2000.0
                for i in range(self.NUM_LEDS):
                    hue = float(i) / self.NUM_LEDS
                    self.strip.set_hsv(i, hue + offset, 1.0, 1.0)
                await uasyncio.sleep(1.0 / UPDATES)
        uasyncio.run(self.timed_effect(time, rainbow_effect))

    def spooky_rainbows(self, time):
        def spooky_rainbow_effect():
            HUE_START = 30  # orange
            HUE_END = 140  # green
            SPEED = 0.3  # bigger = faster (harder, stronger)
            distance = 0.0
            direction = SPEED
            while True:
                for i in range(self.NUM_LEDS):
                    # generate a triangle wave that moves up and down the LEDs
                    j = max(0, 1 - abs(distance - i) / (self.NUM_LEDS / 3))
                    hue = HUE_START + j * (HUE_END - HUE_START)
                    self.strip.set_hsv(i, hue / 360, 1.0, 0.8)
                # reverse direction at the end of colour segment to avoid an abrupt change
                distance += direction
                if distance > self.NUM_LEDS:
                    direction = - SPEED
                if distance < 0:
                    direction = SPEED
            await uasyncio.sleep(0.01)
        uasyncio.run(self.timed_effect(time, spooky_rainbow_effect))

    MORSE_CODE_DICT = { 'A':'.-', 'B':'-...', 'C':'-.-.', 'D':'-..',
        'E':'.', 'F':'..-.', 'G':'--.', 'H':'....', 'I':'..', 'J':'.---',
        'K':'-.-', 'L':'.-..', 'M':'--', 'N':'-.', 'O':'---', 'P':'.--.',
        'Q':'--.-', 'R':'.-.', 'S':'...', 'T':'-', 'U':'..-', 'V':'...-',
        'W':'.--', 'X':'-..-', 'Y':'-.--', 'Z':'--..', '1':'.----',
        '2':'..---', '3':'...--', '4':'....-', '5':'.....', '6':'-....',
        '7':'--...', '8':'---..', '9':'----.', '0':'-----', ', ':'--..--',
        '.':'.-.-.-', '?':'..--..', '/':'-..-.', '-':'-....-',
        '(':'-.--.', ')':'-.--.-', '!':'-.-.--'}

    def moorse(self, phrase, color):
        for word in phrase.split():
            for letter in word.upper():
                print(letter, end=" ")
                for l in self.MORSE_CODE_DICT[letter]:
                    print(l, end="")
                    if l == '.':
                        self.flash(*color)
                        block_sleep(1)
                    else: #dash
                        self.flash(*color)
                        block_sleep(2)
                    self.flash(0,0,0)
                    block_sleep(1)
                print()
                block_sleep(1.5)
            print()

# Colors
cos_blue = (1, 22, 137)
cos_yellow = (246, 209, 6)
