# Set up the Plasma2040
from plasma import plasma_stick
from plasma import WS2812, COLOR_ORDER_RGB
strip = WS2812(50, 0, 0, plasma_stick.DAT, color_order=COLOR_ORDER_RGB)
strip.start()

# Phase 1
from colors import yellow, blue
from moorse import moorse
from time import sleep
while True:
    for word in "33COS WIFI".split():
        moorse(strip, word, blue, yellow)
        sleep(3.3)