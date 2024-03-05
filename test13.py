from network_manager import NetworkManager
import uasyncio
from microdot import Microdot

wifi = NetworkManager("ATTBRyYu7C", "t84dyhw?4m9t")
print("connecting")
wifi.connect()
#uasyncio.sleep(5)
if wifi._sta_if.isconnected(): #success!
    print("connected!")
    print(wifi.ifaddress())
    #connect.cancel()
else:
    print("could not connect")


app = Microdot()

@app.route('/')
async def index(request):
    print(request.method, request.client_addr)
    return f'Hello, {request.client_addr[0]}!'

app.run()