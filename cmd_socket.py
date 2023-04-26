# install & getting started - https://python-socketio.readthedocs.io/en/latest/client.html
# pip install "python-socketio[asyncio_client]==4.6.1"
# ERR - socketio.exceptions.ConnectionError: OPEN packet not returned by server
# Sol - https://stackoverflow.com/questions/66809068/python-socketio-open-packet-not-returned-by-the-server

import functools
print = functools.partial(print, flush=True)

import asyncio
import socketio
import os
import json
import cmd_manager
import sys

# relative file path
if getattr(sys, 'frozen', False):
    __dirname__ =os.path.join(sys._MEIPASS,"..","..") # runned as a .exe file
else:
    __dirname__ =os.path.dirname(os.path.realpath(__file__)) # runned as a .py file

__filename_SP__ = os.path.join(__dirname__,"src","config","ServiceProfile.txt")



# sio = socketio.AsyncClient()
sio = socketio.AsyncClient(engineio_logger=True,logger=True,ssl_verify=False)

@sio.event
async def message(data):
    print('received a message!', data)

@sio.event
async def connect():
    print("socket connected!")

@sio.event
async def disconnect():
    cmd_manager.toHome()
    print("socket disconnected!")

@sio.on('msg-v2')
async def on_message(msg):
    #print("msg-v2(in):",msg,"\n")
    packet=json.loads(msg["message"])
    if packet["type"] == "DUP":
        cmd_manager.update_commandFile(packet["data"])
    elif packet["type"] == "CONFIG":
        cmd_manager.update_config(packet["data"])
    elif packet["type"] == "SIG":
        print("SIG:",json.dumps(packet["data"]))
    else:
        print("unclassifed packet received!:")
        print(packet)
 

async def main():
    await sio.connect(url='https://api.portal301.com', transports = 'websocket')
    #await sio.connect(url='https://192.168.0.11:3333',transports='websocket')

    with open(__filename_SP__, "r") as file:
        serviceProfile=json.load(file)
        # serviceProfile['sid']=sio.sid
        # serviceProfile['socketId']=sio.sid
        # serviceProfile['room']='room:'+sio.sid
        # serviceProfile["robot"]["state"]["socketId"]={"socketId":sio.sid,"roomId":"room:"+sio.sid}
        serviceProfile["robot"]["state"]["socketId"]=sio.sid
        serviceProfile["robot"]["state"]["roomId"]="room:"+sio.sid
    await sio.emit('Start_Service', json.dumps(serviceProfile["robot"]))
    # task = sio.start_background_task(my_background_task, 123)
    await sio.wait()

print('starting socket.io-client')
async def my_background_task(my_argument):
    while True:
        await sio.emit('echo', 'test message')
        await sio.sleep(10)
    # do some background work here!

# async def main():
#     pass

if __name__ =="__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
