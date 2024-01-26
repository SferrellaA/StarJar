import rp2
import network
import machine
import uasyncio
from display import *

class NetworkManager:
    def __init__(self, ssid, psk):
        rp2.country("US")
        self._sta_if = network.WLAN(network.STA_IF)
        self._mode = network.STA_IF
        self._client_timeout = 10
        self._ssid = ssid
        self._psk = psk
        self._error_handler = None
        self.UID = ("{:02X}" * 8).format(*machine.unique_id())

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
        #global checkPointOne
        self._sta_if.active(True)
        #for attempt in range(1,6):
        while not self._sta_if.isconnected():
            self._sta_if.connect(self._ssid, self._psk)
            #print(f"Connection attempt {attempt}/5")
            print("aaa")
            await uasyncio.sleep(3)
        print("bbb")
        global checkPointOne
        checkPointOne = True
        '''
        if self._sta_if.isconnected():
            #print(f"\nConnected to {self._ssid}")
            print("bbb")
            global checkPointOne
            checkPointOne = True
            return
        '''
        '''
        else:
            #print(f"Could not connect to {self._ssid}")
            print("ccc")
            #checkPointOne = False
            uasyncio.sleep(3)
        '''
