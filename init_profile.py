import os
import json
import random
import string

# relative file path
__dirname__ =os.path.dirname(os.path.realpath(__file__))
__filename_SN__ = os.path.join(__dirname__,"config","SerialNumber.txt")
__filename_SP__ = os.path.join(__dirname__,"config","ServiceProfile.txt")


serviceProfile = {
    'sid':'',
    'type':'ROBOT',
    'nickname':'RobotArm_0000',
    'description':'RobotArm',
    'contents':{'stream':['video'],'motor':['7-DOF robot arm', '4-DOF ground vehicle']},
    'owner':'PORTAL301',
    'state':{'socketId':'----'},
}

if os.path.isfile(__filename_SN__):
    with open(__filename_SN__, "r") as file:
        SerialNumber=file.readline()
        print("Serial number is already exist:", SerialNumber)
else:
    with open(__filename_SN__, "w") as file:
        #generate random serial number length with uppser-case letters and digits
        characters = string.ascii_uppercase + string.digits
        SerialNumber = serviceProfile['owner']+"/"+serviceProfile['type']
        SerialNumber+='-0000'
        for i in range(4):
            SerialNumber+='-'+''.join(random.choice(characters) for i in range(4))
        print("Issued Serial Number:", SerialNumber)
        file.write(SerialNumber)

serviceProfile['sid'] = SerialNumber

with open(__filename_SP__, "w") as file:
    json.dump(serviceProfile, file, indent = 4)
    print("Saved the service profile:")
    print(serviceProfile)


