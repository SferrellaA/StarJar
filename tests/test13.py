from network_manager import NetworkManager
import uasyncio
from microdot import Microdot

try:
    import WIFI_CONFIG
    SSID = WIFI_CONFIG.SSID
    PSK = WIFI_CONFIG.PSK
except:
    print("excepted")
    SSID = "Tigers99"
    PSK = "Tigers99"
wifi = NetworkManager(SSID, PSK)

print("connecting")
wifi.connect()
uasyncio.sleep(3)
if wifi._sta_if.isconnected(): #success!
    print("connected!")
    print(wifi.ifaddress())
else:
    print("could not connect")


app = Microdot()

@app.route('/')
async def index(request):
    print(request.method, request.client_addr)
    return f'Hello, {request.client_addr[0]}!'

app.run()