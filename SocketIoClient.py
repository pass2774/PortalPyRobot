# install & getting started - https://python-socketio.readthedocs.io/en/latest/client.html
# ERR - socketio.exceptions.ConnectionError: OPEN packet not returned by server
# Sol - https://stackoverflow.com/questions/66809068/python-socketio-open-packet-not-returned-by-the-server
import asyncio
import socketio
import time


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
    0:[ -30,30],
    1:[ -30,30],
    2:[ -120,120],
  }
  ,"arm":{
    0:[ 100,8000],
    1:[1000,4000],
    2:[ 600,1500],
    3:[ 600,2000],
    4:[1300,2600],
    5:[2300,2900]
  }
}

try:
  file = open("output.txt", "x")
except:
  print("command file(output.txt) already exist. continuing..")
else:
  idx = 0
  arm = '{0:%d,1:%d,2:%d,3:%d,4:%d,5:%d}' % (100,1000,600,600,1300,2300)
  gimbal = '{0:%d,1:%d,2:%d}' % (0,0,0)
  str_cmd = '{"idx":%d,"arm":%s,"gimbal":%s}' % (idx,arm,gimbal)
  file.write(str_cmd)
  file.close()


def read_commandFile(b_print):
  file = open("output.txt", "r")
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



sio = socketio.AsyncClient()

@sio.event
async def connect():
    print('connection established')

@sio.event
async def message(data):
    print('message:', data)
    await sio.emit('response', {'response': 'my response'})

@sio.event
async def disconnect():
    print('disconnected from server')

@sio.on('')
async def catch_all(event, data):
    print('message received: ', data)
    pass

@sio.on('Greetings')
async def on_message(data):
    print('I received a message!', data)

@sio.on('command')
async def on_message(data):
    print('I received a command', data)

async def main():
    print('HAHAHA!!\n')
    # await sio.connect('http://localhost:5000')
    await sio.connect('http://192.168.0.2:3000')
    print('HAHA')
    await sio.emit('SetParams', 'good haha')
    task = sio.start_background_task(my_background_task, 123)
    await sio.wait()

print('starting sio')
fn = 'output.csv'
async def my_background_task(my_argument):
    while True:
        # await sio.emit('SetParams', 'good')
        file = open("output.txt", "r")
        while True:
            line = file.readline()
            if not line:
                break
            print(line)
            await sio.emit('SetParams', line)

        file.close()
        await sio.sleep(0.05)
    # do some background work here!

asyncio.run(main())

# if __name__ == '__main__':
#     asyncio.run(main())

def update_commandFile(input_obj):
    print("before:")    
    data_dict = read_commandFile(True)
    idx=data_dict["idx"]+1

    # Data range verification
    isCmdValid = verify_commandRange(input_obj, valid_range)

    # Update command file    
    if not isCmdValid:
        print('The input command is ignored.','(out of range error')  
    else:
        str_cmd = '{"idx":%d,"arm":%s,"gimbal":%s}' % (idx,arm,gimbal)
        with open("output.txt", "w") as file:
            file.write(str_cmd)
        print("after:")    
        data_dict = read_commandFile(True)


arm = '{0:%d,1:%d,2:%d,3:%d,4:%d,5:%d}' % (4000,1000,900,600,1300,2300)
gimbal = '{0:%d,1:%d,2:%d}' % (0,0,0)
arm = '{0:%d,1:%d,2:%d,3:%d,4:%d,5:%d}' % (6000,4000,1500,2000,2600,2900)
gimbal = '{0:%d,1:%d,2:%d}' % (30,0,100)
input_data_dict ={
"arm":eval(arm), # eval('str') --> dict
"gimbal":eval(gimbal),
}

update_commandFile(input_data_dict)
