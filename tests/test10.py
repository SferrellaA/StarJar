import uasyncio
from display import *
from time import sleep

async def counter(j):
    i = 1
    while i <= j:
        print(i)
        await uasyncio.sleep(i)
        i += 1

async def main():
    display = LED_Strip(50)
    
    fire = uasyncio.create_task(display.fire())
    await uasyncio.sleep(0)
    await counter(1)
    fire.cancel()
    display.flash(0,0,0)
    
    spooky_rainbow = uasyncio.create_task(display.spooky_rainbows())
    await uasyncio.sleep(0)
    await counter(1)
    spooky_rainbow.cancel()
    display.flash(0,0,0)
    
    sparkle = uasyncio.create_task(display.sparkle())
    await uasyncio.sleep(0)
    await counter(3)
    sparkle.cancel()
    display.flash(0,0,0)
    
    rainbow = uasyncio.create_task(display.rainbow())
    await uasyncio.sleep(0)
    await counter(2)
    rainbow.cancel()
    display.flash(0,0,0)
    
    print("dooone")

uasyncio.run(main())

