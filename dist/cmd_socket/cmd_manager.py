# install & getting started - https://python-socketio.readthedocs.io/en/latest/client.html
# pip install "python-socketio[asyncio_client]==4.6.1"
# ERR - socketio.exceptions.ConnectionError: OPEN packet not returned by server
# Sol - https://stackoverflow.com/questions/66809068/python-socketio-open-packet-not-returned-by-the-server
from time import time
import json
import os

# relative file path
__dirname__ = os.path.dirname(os.path.realpath(__file__))
__filename_log_command__ = os.path.join(__dirname__,"log_command.txt")
__filename_command__ = os.path.join(__dirname__,"command.txt")
__filename_dxl_param__ = os.path.join(__dirname__,"src","calibration","dxl_param.txt")

def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate

@static_vars(mode=False)
def setRecord(arg):
    setRecord.mode = arg
    print("record mode:",setRecord.mode)

@static_vars(start=0)
def timeStamp(arg):
    timeStamp.start = arg
    print("start time:",timeStamp.start)

@static_vars(command=[])
def logger(arg):
    logger.command = arg
    print("start time:",timeStamp.start)



dxl_param={}
with open((__filename_dxl_param__), "r") as file:
  dxl_param=json.load(file)
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
    5:[ -360,360],
    6:[ -180,180],
  }
}
try:
  file = open(__filename_command__, "x")
except:
  print("command file(command.txt) already exists. continuing..")
else:
  idx = 0
  arm = '{0:%d,1:%d,2:%d,3:%d,4:%d,5:%d,6:%d}' % (0,0,0,0,0,0,0)
  arm = str(dxl_param["home-position"])
  gimbal = '{0:%d,1:%d,2:%d}' % (0,0,0)
  str_cmd = '{"idx":%d,"arm":%s,"gimbal":%s}' % (idx,arm,gimbal)
  file.write(str_cmd)
  file.close()


def read_commandFile(b_print):
  with open(__filename_command__, "r") as file:
    dict = json.load(file)
  if b_print:
    print('cmd:',dict)  
  return dict

def verify_commandRange(data_obj,rangeBook):
  isCmdValid = True
  for title, rangeTable in rangeBook.items():
    for key, range in rangeTable.items():
      if (data_obj[title][key] < range[0]) or (data_obj[title][key] > range[1]):
        isCmdValid=False
        print(bcolors.WARNING+'The input data "', title,'":{',key,':', data_obj[title][key],') is not valid: out of range'+bcolors.ENDC)
  return isCmdValid


log_command = []

def update_commandFile(input_obj,b_print=True):
    data_dict = read_commandFile(False)
    idx=data_dict["idx"]+1
    dict_packet=input_obj
    dict_packet["idx"]=idx

    # Data range verification
    # isCmdValid = verify_commandRange(dict_packet, valid_range)
    isCmdValid = True # Forced to be True during development

    # Update command file    
    if not isCmdValid:
        print('The input command is ignored.','(out of range error)')  
    else:
      with open(__filename_command__, "w") as file:
        json.dump(dict_packet,file,indent = 2)
      if setRecord.mode == True:
        log_command.append({"t0":time()-timeStamp.start,"data":input_obj})
      if b_print:
        data_dict = read_commandFile(True)
      
def update_config(packet):
  if "operation" in packet.keys():
    if packet["operation"]=="CALIBRATION":
      pass
    elif packet["operation"]=="HOME_CALIBRATION":
      pass
    elif packet["operation"]=="TORQUE_OFF":
      pass

  if "record" in packet.keys():
    if packet["record"]=="START":
      timeStamp(time())
      setRecord(True)
      log_command.clear()
    elif packet["record"]=="WRITE":
      setRecord(False)
      with open(__filename_log_command__, "w") as file:
        json.dump(log_command,file,indent = 2)
    elif packet["record"]=="APPEND":
      setRecord(False)
      print("Currently Not Available ")
      # with open(__filename_log_command__, "a") as file:
      #   file.write("")
    elif packet["record"]=="DISCARD":
      setRecord(False)
    elif packet["record"]=="DELETE":
      setRecord(False)
      with open(__filename_log_command__, "w") as file:
        file.write("")


    


def toHome():
  input_data_dict ={
    "arm":dxl_param["home-position"], 
    "gimbal":{0:0,1:0,2:0},
    "gv:":{21:0,22:0,23:0,24:0}
  }
  update_commandFile(input_data_dict)