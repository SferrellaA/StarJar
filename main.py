from network_manager import NetworkManager
import uasyncio
from display import *
from microdot import Microdot

# If WIFI_CONFIG.py exists it will skip part 1
try:
    import WIFI_CONFIG
    SSID = WIFI_CONFIG.SSID
    PSK = WIFI_CONFIG.PSK
except:
    SSID = "Tigers99"
    PSK = "Tigers99"
wifi = NetworkManager(SSID, PSK)

display = LED_Strip(50)

async def timer(time, command, *args):
    task = uasyncio.create_task(command(*args))
    await uasyncio.sleep(time)
    task.cancel()

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
        break # conncted
    else: # not connected
        print(f"Could not connect to {wifi._ssid}")
        await timer(3, display.fire)

# Set up the web server
app = Microdot()
import web.routes
import web.hidden
import web.get
app.run()

# TODO - handle high scores