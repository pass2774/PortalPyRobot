import sys
import os
import json
import random
import string

# relative file path
if getattr(sys, 'frozen', False):
    __dirname__ =os.path.join(sys._MEIPASS,"..","..") # runned as a .exe file
else:
    __dirname__ =os.path.dirname(os.path.realpath(__file__)) # runned as a .py file

__filename_SN__ = os.path.join(__dirname__,"src","config","SerialNumber.txt")
__filename_SP__ = os.path.join(__dirname__,"src","config","ServiceProfile.txt")



# serviceProfile = {
#     'sid':'',
#     'spw':'0000',
#     'type':'ROBOT',
#     'nickname':'RobotArm_0000',
#     'description':'RobotArm',
#     'contents':{'stream':['video'],'motor':['7-DOF robot arm', '4-DOF ground vehicle']},
#     'owner':'PORTAL301',
#     'state':{'socketId':'----'},
# }

serviceProfile = {
    "cluster":{
        "sid":"",
        "spw":"0000",
        "type":"CLUSTER",
        "nickname":"plantWatcher-0000",
        "description":"service-cluster-plantWatcher",
        "owner":"PORTAL301",
        "contents":{},
        "state":{
            "ch0":{"sid":"XXXX-XXXX-XXXX-XXXX"},
            "ch1":{"sid":"XXXX-XXXX-XXXX-XXXX"}
            }
    },
    "robot":{
        "sid":"",
        "spw":None,
        "type":"ROBOT",
        "nickname":None,
        "description":"dolly and arm",
        "_robotClass":"plantWatcher",
        "owner":None,
        "contents":['3-DOF robot arm', '1-DOF dolly'],
        "state":{"isClustered":True,"cid":"----","socketId":"----","roomId":"----"}
    },
    "camera":{
        "sid":"",
        "spw":None,
        "type":"CAMERA",
        "nickname":None,
        "description":"RobotCam",
        "owner":None,
        "contents":['video'],
        "state":{"isClustered":True,"cid":"----","socketId":"----","roomId":"----"}
    }
}

# serviceProfile_robot = {
#     "sid":"",
#     "spw":"0000",
#     "type":"ROBOT",
#     "nickname":"",
#     "description":"RobotArm",
#     "owner":"",
#     "contents":['7-DOF robot arm', '4-DOF ground vehicle'],
#     "state":{"cid":"----","socketId":"----","roomId":"----"}
# }
# serviceProfile_cam = {
#     "sid":"",
#     "spw":"0000",
#     "type":"CAMERA",
#     "nickname":"",
#     "description":"RobotCam",
#     "owner":"",
#     "contents":['video'],
#     "state":{"cid":"----","socketId":"----","roomId":"----"}
# }



if os.path.isfile(__filename_SN__):
    with open(__filename_SN__, "r") as file:
        SerialNumber=file.readline()
        print("Serial number already exists:", SerialNumber)
else:
    with open(__filename_SN__, "w") as file:
        #generate random serial number length with uppser-case letters and digits
        characters = string.ascii_uppercase + string.digits
        SerialNumber = serviceProfile['cluster']['owner']+"/"+serviceProfile['cluster']['type']
        SerialNumber+='-0000'
        for i in range(4):
            SerialNumber+='-'+''.join(random.choice(characters) for i in range(4))
        print("Issued Serial Number:", SerialNumber)
        file.write(SerialNumber)

serviceProfile["cluster"]["sid"] = SerialNumber
serviceProfile["robot"]["sid"] = SerialNumber+":0"
serviceProfile["camera"]["sid"] = SerialNumber+":1"

serviceProfile["cluster"]["state"]["ch0"]["sid"] = serviceProfile["robot"]["sid"]
serviceProfile["cluster"]["state"]["ch1"]["sid"] = serviceProfile["camera"]["sid"]
serviceProfile["cluster"]["contents"]["ch0"] = serviceProfile["robot"]["contents"]
serviceProfile["cluster"]["contents"]["ch1"] = serviceProfile["camera"]["contents"]

serviceProfile["robot"]["state"]["cid"] = serviceProfile["cluster"]["sid"]
serviceProfile["camera"]["state"]["cid"] = serviceProfile["cluster"]["sid"]

# arbitrarily defined properties for child services
serviceProfile["robot"]["nickname"] = serviceProfile["cluster"]["nickname"]+":"+serviceProfile["robot"]["type"]
serviceProfile["camera"]["nickname"] = serviceProfile["cluster"]["nickname"]+":"+serviceProfile["camera"]["type"]
serviceProfile["robot"]["owner"] = serviceProfile["cluster"]["owner"]
serviceProfile["camera"]["owner"] = serviceProfile["cluster"]["owner"]

with open(__filename_SP__, "w") as file:
    json.dump(serviceProfile, file, indent = 4)
    print("Saved the service profile:")
    print(serviceProfile)


