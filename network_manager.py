import rp2
import network
import machine
import uasyncio
from display import *
from time import sleep as block_sleep

#display = LED_Strip(50)

class NetworkManager:
    #_ifname = ("Client", "Access Point")

    def __init__(self, ssid, psk):
        rp2.country("US")
        #self._ap_if = network.WLAN(network.AP_IF)
        self._sta_if = network.WLAN(network.STA_IF)
        self._mode = network.STA_IF
        self._client_timeout = 10
        self._ssid = ssid
        self._psk = psk
        self._error_handler = None
        self.UID = ("{:02X}" * 8).format(*machine.unique_id())

    '''
    def config(self, var):
        if self._sta_if.active():
            return self._sta_if.config(var)
        else:
            if var == "password":
                return self.UID
            return self._ap_if.config(var)

    def mode(self):
        if self._sta_if.isconnected():
            return self._ifname[0]
        if self._ap_if.isconnected():
            return self._ifname[1]
        return None
    '''

    def ifaddress(self):
        if self._sta_if.isconnected():
            return self._sta_if.ifconfig()[0]
        if self._ap_if.isconnected():
            return self._ap_if.ifconfig()[0]
        return '0.0.0.0'

    def disconnect(self):
        if self._sta_if.isconnected():
            self._sta_if.disconnect()
        if self._ap_if.isconnected():
            self._ap_if.disconnect()
    
    async def connect(self):
        self._sta_if.active(True)
        self._sta_if.connect(self._ssid, self._psk)
        for attempt in range(1,6):
            print(f"Connection attempt {attempt}/5")
            if self._sta_if.isconnected():
                print(f"Connected to {self._ssid}")
                return True
            await uasyncio.sleep(attempt) # crude backoff
        else:
            print(f"Could not connect to {self._ssid}")
            return False
'''
async def flash_loop(display):
    while True:
        display.flash(*cos_yellow)
        await uasyncio.sleep(1)
        display.flash(*cos_blue)
        await uasyncio.sleep(1)
        
# set up wifi
async def main():
    wifi = NetworkManager("fake network", "ddd")
    display.moorse("I", (255, 255, 255))

    task = uasyncio.create_task(flash_loop(display))
    await uasyncio.sleep(0)
    await wifi.connect()
    task.cancel()
    display.flash(0,0,0)
uasyncio.run(main())
'''