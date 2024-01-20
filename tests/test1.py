import plasma
from plasma import plasma_stick
import time
from random import random, uniform
from rgb_to_hsv import rgb_to_hsv

# Set how many LEDs you have
NUM_LEDS = 50

# WS2812 / NeoPixel™ LEDs
led_strip = plasma.WS2812(NUM_LEDS, 0, 0, plasma_stick.DAT, color_order=plasma.COLOR_ORDER_RGB)

# Start updating the LED strip
led_strip.start()

while True:
    h,s,v = rgb_to_hsv(1, 22, 137)
    for i in range(NUM_LEDS):
        led_strip.set_hsv(i, h, s, v)
    time.sleep(1)
    h, s, v = rgb_to_hsv(246, 209, 6)
    for i in range(NUM_LEDS):
        led_strip.set_hsv(i, h, s, v)
    time.sleep(1)
