# install & getting started - https://python-socketio.readthedocs.io/en/latest/client.html
# pip install "python-socketio[asyncio_client]==4.6.1"
# ERR - socketio.exceptions.ConnectionError: OPEN packet not returned by server
# Sol - https://stackoverflow.com/questions/66809068/python-socketio-open-packet-not-returned-by-the-server
import asyncio
import socketio
import time


dxl_param={}
with open("dxl_param.txt", "r") as file:
  dxl_param=eval(file.readline())
print("dxl_param reading success!")


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
valid_range ={
  "gimbal":{
    0:[ -90,90],
    1:[ -40,40],
    2:[ -180,180],
  }
  ,"arm":{
    0:[ -180,180],
    1:[ -180,180],
    2:[ -180,180],
    3:[ -180,180],
    4:[ -180,180],
    5:[ -180,180],
  }
}
try:
  file = open("output.txt", "x")
except:
  print("command file(output.txt) already exists. continuing..")
else:
  idx = 0
  arm = '{0:%d,1:%d,2:%d,3:%d,4:%d,5:%d}' % (0,0,0,0,0,0)
  arm = str(dxl_param["home-position"])
  gimbal = '{0:%d,1:%d,2:%d}' % (0,0,0)
  str_cmd = '{"idx":%d,"arm":%s,"gimbal":%s}' % (idx,arm,gimbal)
  file.write(str_cmd)
  file.close()


def read_commandFile(b_print):
  file = open("./output.txt", "r")
  for line in file.readlines():
    dict=eval(line)
    if b_print:
      print('dict["idx"]-->',dict["idx"])
      print('dict["arm"]-->',dict["arm"])
      print('dict["gimbal"]-->',dict["gimbal"])  
  return dict

def verify_commandRange(data_obj,rangeBook):
  isCmdValid = True
  for title, rangeTable in rangeBook.items():
    for key, range in rangeTable.items():
      if (data_obj[title][key] < range[0]) or (data_obj[title][key] > range[1]):
        isCmdValid=False
        print(bcolors.WARNING+'The input data "', title,'":{',key,':', data_obj[title][key],') is not valid: out of range'+bcolors.ENDC)
  return isCmdValid


def update_commandFile(input_obj,b_print=True):
    data_dict = read_commandFile(False)
    idx=data_dict["idx"]+1

    packet=eval(input_obj)
    dict_packet={}
    dict_packet["idx"]=idx
    dict_packet["arm"]=eval(packet["arm"])
    dict_packet["gimbal"]=eval(packet["gimbal"])
    # Data range verification
    isCmdValid = verify_commandRange(dict_packet, valid_range)

    # Update command file    
    if not isCmdValid:
        print('The input command is ignored.','(out of range error)')  
    else:
        # str_cmd = '{"idx":%d,"arm":%s,"gimbal":%s}' % (idx,arm,gimbal)
        str_cmd = str(dict_packet)
        with open("output.txt", "w") as file:
          file.write(str_cmd)
        if b_print:
          data_dict = read_commandFile(True)


arm_str = '{0:%d,1:%d,2:%d,3:%d,4:%d,5:%d}' % (0,0,0,0,0,0)
arm_str = str(dxl_param["home-position"])
gimbal_str = '{0:%d,1:%d,2:%d}' % (0,0,0)
input_data_dict ={
"arm":arm_str, # eval('str') --> dict
"gimbal":gimbal_str,
}

update_commandFile(str(input_data_dict))




import socketio
import asyncio
import json

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
    print("socket disconnected!")

@sio.on('msg-v2')
async def on_message(data):
   update_commandFile(str(data.get("message")))
 

async def main():
    # await sio.connect('http://localhost:5000')
    # await sio.connect(url='https://portal301.com', transports = 'websocket')
    await sio.connect(url='https://192.168.0.2:3333',transports='websocket')
    
    serviceProfile = {
        'socketId':sio.sid,
        'room':'room:'+sio.sid,
        'type':'robot',
        'description':'robot',
        'contents':{'stream':'{video,audio}'}
        }
    await sio.emit('Start_Service', json.dumps(serviceProfile))
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
    asyncio.run(main())