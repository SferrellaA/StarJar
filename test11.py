from network_manager import NetworkManager
import uasyncio
from display import *
#from time import sleep

display = LED_Strip(50)
wifi = NetworkManager("Tigers99", "Tigers99")

global checkPointOne
checkPointOne = False

async def timer(time, command, *args):
    task = uasyncio.create_task(command(*args))
    await uasyncio.sleep(time)
    task.cancel()

async def part1():
    # Startup
    #await timer(3, display.rainbow)
    connect = uasyncio.create_task(wifi.connect())
    
    # The regular loop
    while True:
        display.flash(0,0,0)
        global checkPointOne
        await display.moorse("I")
        
        if wifi._sta_if.isconnected():
            connect.cancel()
            print(f"\nConnected to {wifi._ssid}")
            await timer(3, display.rainbow)
            return
        else:
            print(f"Could not connect to {wifi._ssid}")
            await timer(3, display.fire)
        '''        
        uasyncio.gather(wifi.connect())
        task = uasyncio.create_task(display.flash_loop())
        connection = await wifi.connect()
        task.cancel()
        
        # Connection Successfuul
        if connection:
            display.flash(0,0,0)
            return
        else:
        '''
uasyncio.run(part1())
print("here")