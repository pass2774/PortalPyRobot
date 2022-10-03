#pip install requests
# pip install python-socketio[asyncio_client]==4.6.1
from asyncio import transports
import requests

print("hello")

host = 'https://search.naver.com'
path = '/search.naver'
params = {'query':'icecream'}

# url = host+path
url = "https://portal301.com"
response = requests.get(url,params=params)
# print(response.content)

import socketio
import asyncio
import json

# sio = socketio.AsyncClient()
sio = socketio.AsyncClient(engineio_logger=True,logger=True,ssl_verify=False)

@sio.event
async def message(data):
    print('I received a message!')


@sio.event
async def connect():
    print("socket io connected!")

@sio.event
async def disconnect():
    print("socket disconnected!")

@sio.on('command')
async def on_message(data):
    print('I received a command', data)
@sio.on('terminate')
async def on_message(data):
    print('I received a command', data)

async def main():
    # await sio.connect('http://localhost:5000')
    await sio.connect(url='https://api.portal301.com', transports = 'websocket')

    # await sio.connect(url='https://192.168.0.2:3333',transports='websocket')
    print('starting socket.io-client')

    serviceProfile = {
        'socketId':sio.sid,
        'room':'room:'+sio.sid,
        'type':'robot',
        'description':'robot',
        'contents':{'stream':'{video,audio}'}
        }
    await sio.emit('Start_Service', json.dumps(serviceProfile))
    task = sio.start_background_task(my_background_task, 123)
    await sio.wait()

print('starting sio')
async def my_background_task(my_argument):
    while True:
        await sio.emit('echo', 'test message')
        await sio.sleep(10)
    # do some background work here!

# async def main():
#     pass

if __name__ =="__main__":
    asyncio.run(main())