import rp2
import network
import machine
import uasyncio
from display import *
from time import sleep as block_sleep

display = LED_Strip(50)

stage = 1

class NetworkManager:
    _ifname = ("Client", "Access Point")

    def __init__(self, ssid, psk): #, error_effect):
        rp2.country("US")
        self._ap_if = network.WLAN(network.AP_IF)
        self._sta_if = network.WLAN(network.STA_IF)
        self._mode = network.STA_IF
        self._client_timeout = 10
        self._ssid = ssid
        self._psk = psk
        #self._error_effect = error_effect
        #self._access_point_timeout = access_point_timeout
        self._error_handler = None
        self.UID = ("{:02X}" * 8).format(*machine.unique_id())

    def isconnected(self):
        return self._sta_if.isconnected() or self._ap_if.isconnected()

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

    async def wait(self, mode):
        while not self.isconnected():
            self._handle_status(mode, None)
            await uasyncio.sleep_ms(1000)

    def _handle_status(self, mode, status):
        # reports wifi connection status
        print(self._ifname[mode], status, self.ifaddress())
        print('Connecting to ' + self._ssid)
        
        # flash while connecting
        #display.flash(255, 255, 255) # This needs to be out of the network functions
        #block_sleep(0.02)
        #display.flash(0,0,0)
        
        if status is not None:
            if status:
                print('Wifi connection successful!')
            else:
                print('Wifi connection failed!')
                # if no wifi connection, you get display.spooky rainbows. Bwahahaha!
                #display.spooky_rainbows(5)
                #self._error_effect(5)

    '''
    def _handle_error(self, mode, msg):
        if callable(self._error_handler):
            if self._error_handler(self._ifname[mode], msg):
                return
        raise RuntimeError(msg)
    '''

    async def connect(self):
        print("starting to connect to wifi")
        
        # Already connected to wifi
        #if self._sta_if.isconnected():
        #    self._handle_status(network.STA_IF, True)
        #    return
        
        # Prep to connect to wifi
        self._ap_if.disconnect()
        self._ap_if.active(False)
        self._sta_if.active(True)
        self._sta_if.connect(self._ssid, self._psk)
        
        # Try to connect to wifi
        try:
            await uasyncio.wait_for(self.wait(network.STA_IF), self._client_timeout)
            #self._handle_status(network.STA_IF, True)
            print("connected to wifi!")
        
        # Connecting to wifi didn't work
        except uasyncio.TimeoutError:
            print("couldn't connect to wifi")
            self._sta_if.active(False)
            #self._handle_status(network.STA_IF, False)
            #self._handle_error(network.STA_IF, "WIFI Client Failed")
            global stage
            stage += 1

async def flash_loop(display):
    while True:
        display.flash(*cos_yellow)
        await uasyncio.sleep(1)
        display.flash(*cos_blue)
        await uasyncio.sleep(1)
        
# set up wifi
async def main():
    #wifi = NetworkManager("ATTBRyYu7C", "t84dyhw?4m9t") #, display.fire)
    wifi = NetworkManager("fake network", "ddd")
    display.moorse("I", (255, 255, 255))

    task = uasyncio.create_task(flash_loop(display))
    await uasyncio.sleep(0)
    print(stage)
    await wifi.connect()
    print(stage)
    task.cancel()
    display.flash(0,0,0)
uasyncio.run(main())