from network_manager import NetworkManager
import uasyncio
from display import *

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
    await timer(3, display.rainbow)
    connect = uasyncio.create_task(wifi.connect())
    
    # The regular loop
    while True:
        # Display the ssid
        display.flash(0,0,0)
        await display.moorse(wifi._ssid)
        
        # Check connection *after* the ssid is displayed
        if wifi._sta_if.isconnected(): #success!
            connect.cancel()
            print(f"\nConnected to {wifi._ssid}")
            await timer(3, display.rainbow)
            return
        else: # not connected
            print(f"Could not connect to {wifi._ssid}")
            await timer(3, display.fire)

uasyncio.run(part1())
print("here")