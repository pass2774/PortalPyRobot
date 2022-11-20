

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
    0:[ -60,60],
    1:[ -30,30],
    2:[ -120,120],
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
  print("command file(output.txt) already exist. continuing..")
else:
  idx = 0
  arm = '{0:%d,1:%d,2:%d,3:%d,4:%d,5:%d}' % (0,0,0,0,0,0)
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


arm = '{0:%d,1:%d,2:%d,3:%d,4:%d,5:%d}' % (0,-60,120,0,0,0)
# arm = '{0:%d,1:%d,2:%d,3:%d,4:%d,5:%d}' % (0,20,0,0,0,0)
gimbal = '{0:%d,1:%d,2:%d}' % (30,0,0)

input_data_dict ={
"arm":eval(arm), # eval('str') --> dict
"gimbal":eval(gimbal),
}

update_commandFile(input_data_dict)