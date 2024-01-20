import colors
from time import sleep
from random import random, uniform
import uasyncio

def clear(strip):
    for led in range(50): 
        strip.set_rgb(led, 0,0,0)

async def timed_effect(time, effect):
    uasyncio.create_task(effect())
    await uasyncio.sleep(time)

def dazzle(intensity, # How much dazzle? [bigger number = more dazzle]
           # Change your colours here! RGB colour picker: https://g.co/kgs/k2Egjk
           background,
           color,
           # how quickly current colour changes to target colour [1 - 255]
           fadeIn,
           fadeOut):
    # Create a list of [r, g, b] values that will hold current LED colours, for display
    current_leds = [[0] * 3 for i in range(NUM_LEDS)]
    # Create a list of [r, g, b] values that will hold target LED colours, to move towards
    target_leds = [[0] * 3 for i in range(NUM_LEDS)]
    
    def display_current():
        # paint our current LED colours to the strip
        for i in range(NUM_LEDS):
            strip.set_rgb(i, current_leds[i][0], current_leds[i][1], current_leds[i][2])
    def move_to_target():
        # nudge our current colours closer to the target colours
        for i in range(NUM_LEDS):
            for c in range(3):  # 3 times, for R, G & B channels
                if current_leds[i][c] < target_leds[i][c]:
                    # increase current, up to a maximum of target
                    current_leds[i][c] = min(current_leds[i][c] + fadeIn, target_leds[i][c])  
                elif current_leds[i][c] > target_leds[i][c]:
                    # reduce current, down to a minimum of target
                    current_leds[i][c] = max(current_leds[i][c] - fadeOut, target_leds[i][c])  
    
    while True:
        for i in range(NUM_LEDS):
            # randomly add sparkles
            if intensity > uniform(0, 1):
                # set a target to start a sparkle
                target_leds[i] = color
            # for any sparkles that have achieved max sparkliness, reset them to background
            if current_leds[i] == target_leds[i]:
                target_leds[i] = background
        move_to_target()   # nudge our current colours closer to the target colours
        display_current()  # display current colours to strip

def sparkle():
    intensity = 0.005 
    background = [50, 50, 0]
    color = [255, 255, 0]
    fadeIn = 2
    fadeOut = 2
    dazzle(intensity, background, color, fadeIn, fadeOut)

def snow():
    intensity = 0.0002
    background = [30, 50, 50]  # dim blue
    color = [240, 255, 255]  # bluish white
    fadeIn = 255  # abrupt change for a snowflake
    fadeOut = 1
    dazzle(intensity, background, color, fadeIn, fadeOut)

def rainbow(time):
    async def rainbow_effect():
        SPEED = 20 # The SPEED that the LEDs cycle at (1 - 255)
        UPDATES = 60 # How many times the LEDs will be updated per second
        offset = 0.0
        while True:
            SPEED = min(255, max(1, SPEED))
            offset += float(SPEED) / 2000.0
            for i in range(NUM_LEDS):
                hue = float(i) / NUM_LEDS
                strip.set_hsv(i, hue + offset, 1.0, 1.0)
            await uasyncio.sleep(1.0 / UPDATES)
    uasyncio.run(timed_effect(time, rainbow_effect))

def fire(time):
    async def fire_effect():
        while True:
            # Random red/orange hue, full saturation, random brightness
            for i in range(NUM_LEDS):
                strip.set_hsv(i, uniform(0.0, 50 / 360), 1.0, random())
            await uasyncio.sleep(0.1)
    uasyncio.run(timed_effect(time, fire_effect))

# Set up the Plasma2040
from plasma import plasma_stick
from plasma import WS2812, COLOR_ORDER_RGB
NUM_LEDS = 50
strip = WS2812(NUM_LEDS, 0, 0, plasma_stick.DAT, color_order=COLOR_ORDER_RGB)
strip.start()

rainbow(2)
clear(strip)
sleep(4)
fire(5)
rainbow(2)