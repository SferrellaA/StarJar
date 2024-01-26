from network_manager import NetworkManager
import uasyncio
from display import *
from random import randint
#from time import sleep

display = LED_Strip(50)
wifi = NetworkManager("Tigers99", "Tigers99")

async def timer(time, command, *args):
    task = uasyncio.create_task(command(*args))
    await uasyncio.sleep(time)
    task.cancel()

async def part1():
    # Startup
    await timer(3, display.rainbow)
    
    # The regular loop
    while True:
        display.flash(0,0,0)
        display.moorse("I", (randint(1,255),randint(1,255),randint(1,255)))
        task = uasyncio.create_task(display.flash_loop())
        connection = await wifi.connect()
        task.cancel()
        
        # Connection Successfuul
        if connection:
            display.flash(0,0,0)
            return

uasyncio.run(part1())
print("here")