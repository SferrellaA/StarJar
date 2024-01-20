import uasyncio
from display import *
from time import sleep

async def count_to_five():
    i = 1
    while i <= 5:
        print(i)
        await uasyncio.sleep(i)
        i += 1

async def flash_loop(display):
    while True:
        display.flash(*cos_yellow)
        await uasyncio.sleep(1)
        display.flash(*cos_blue)
        await uasyncio.sleep(1)

async def main():
    display = LED_Strip(50)
    print("starting")
    task = uasyncio.create_task(flash_loop(display))
    await uasyncio.sleep(0)
    await count_to_five()
    print("ending")
    task.cancel()
    display.flash(0,0,0)
    print("dooone")
    #await bar(1)  # Pauses here until bar is complete
    #task = asyncio.create_task(bar(5))
    #await asyncio.sleep(0)  # bar has now started
    #print('Got here: bar running')  # Can run code here
    #await task  # Now we wait for the bar task to complete
    #print('All done')
    '''
    display = LED_Strip(50)
    print("flash for 3")
    try:
        await uasyncio.wait_for(flash_loop(display), 3)
    except uasyncio.TimeoutError:
        print("done")
    loop = uasyncio.create_task(flash_loop(display))
    count_to_five()
    loop.stop()
    print("done")
    '''
uasyncio.run(main())



'''
try:
    fl = loop
    co = loop.create_task(count_to_five())
    loop.run_forever()
    await co
    screen.stop()
    #uasyncio.run(flash_loop(display))
    #uasyncio.run_until_complete(count_to_five())
except Exception as e: # uasyncio.TimeoutError:
    print(f"{e}")
    loop.stop()
    display.flash(*cos_blue)
    sleep(1)
    display.flash(0,0,0)
'''