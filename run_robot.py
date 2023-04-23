#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
# Copyright 2022 PORTAL301 CO., LTD.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

#stderr do not use buffering, but stdout use buffering.
#Therefore, we need to set flush=True to 'pipe' stdout from external program.
import functools
print = functools.partial(print, flush=True) 

import os
import sys
from pickle import FALSE
import numpy as np
import time
import json
sys.path.append("./src")
from dxl_registerMap import *

if os.name == 'nt':
    import msvcrt
    def getch():
        return msvcrt.getch().decode()
else:
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    def getch():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

from dynamixel_sdk import *                    # Uses Dynamixel SDK library


_availableRobotClass = ["robotArm","plantWatcher"]

if len(sys.argv) < 2 :
  print("INPUT ERROR: Input _robotClass")
  print("Available robotClass ->")
  print(_availableRobotClass)
  quit()
elif not sys.argv[1] in _availableRobotClass:
  print("INPUT ERROR: Wrong input.")
  quit()

_robotClass = sys.argv[1]
print("class:")
print(_robotClass)


# relative file path
if getattr(sys, 'frozen', False):
    __dirname__ =os.path.join(sys._MEIPASS,"..","..") # runned as a .exe file
else:
    __dirname__ =os.path.dirname(os.path.realpath(__file__)) # runned as a .py file
__filename_Comport__ = os.path.join(__dirname__,"src","config","Comport.txt")
__filename_flag__ = os.path.join(__dirname__,"flag.txt")
# __filename_command__ = os.path.join(__dirname__,"command.txt")
__filename_SP__ = os.path.join(__dirname__,"src","config","ServiceProfile.txt")
with open(__filename_SP__, "r") as file:
  serviceProfile=json.load(file)
  _robotClass=serviceProfile["robot"]["_robotClass"]
  __filename_command__ = os.path.join(__dirname__,"cmd_"+_robotClass+".txt")




with open(os.path.join(__dirname__,"src","calibration","dxl_param.txt"), "r") as file:
  dxl_param=json.load(file)

print(dxl_param)
print("*****\n_robotClass:\n")
print(_robotClass)
print("*****\n??robotArm??\n")
print(dxl_param['robotArm'])
print("*****\n??dxl_param[robotClass]??\n")
# dxl_default_angle = {0:0,1:-50,2:130,3:0,4:0,5:0}
param_robotClass = dxl_param[_robotClass]
print(param_robotClass)
dxl_pos_control = param_robotClass["dxl-pos-control"]
dxl_id_pos=[int(id) for id in param_robotClass["dxl-pos-control"].keys()]
dxl_id_vel=[int(id) for id in param_robotClass["dxl-vel-control"].keys()]
home_position={id:dxl["home"] for id, dxl in param_robotClass["dxl-pos-control"].items()}
dxl_goal_arm = home_position
dxl_goal_position={}

calib_map={}
#read the calibration map data
with open(os.path.join(__dirname__,"src","calibration","dxl_arm.txt"), "r") as file:
  calib_map["pos"]=json.load(file)
#   calib_map["arm"]=eval(file.readline())
with open(os.path.join(__dirname__,"src","calibration","dxl_gv.txt"), "r") as file:
  calib_map["vel"]=json.load(file)
#   calib_map["gv"]=eval(file.readline())
print("calibration map reading done!")

# with open(os.path.join(__dirname__,"src","config","Comport.txt"), "r") as file:
#   config_comport=eval(file.readline())
with open(__filename_Comport__, "r") as file:
  config_comport=json.load(file)
# Comport Settings
BAUDRATE                 = config_comport['dxlCh0']['baudrate']  # Dynamixel default baudrate : 57600
COMPORT                  = config_comport['dxlCh0']['port']      # Check which port is being used on your controller
                                                                   # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*

def interp_maps(x,map_x,map_y,dtype):
  print("interp_maps")
  print(x)
  print(map_x)
  print(map_y)
  y={}
  for idx, value in x.items():
    if map_x[idx][1]>=map_x[idx][0]:
      y[idx]=np.interp(value,map_x[idx],map_y[idx]).astype(dtype)
    else:
      y[idx]=np.interp(-value,[-map_x[idx][0],-map_x[idx][1]],map_y[idx]).astype(dtype)
  print("done")
  return y






# Initialize PortHandler instance - Set the port path
portHandler = PortHandler(COMPORT)
# Initialize PacketHandler instance - Set the protocol version
packetHandler = PacketHandler(PROTOCOL_VERSION)
# Initialize GroupSync Read & Write instance
groupSyncWritePos = GroupSyncWrite(portHandler, packetHandler, ADDR_PRO_GOAL_POSITION, LEN_PRO_GOAL_POSITION)
groupSyncReadPos = GroupSyncRead(portHandler, packetHandler, ADDR_PRO_PRESENT_POSITION, LEN_PRO_PRESENT_POSITION)
groupSyncWriteVel = GroupSyncWrite(portHandler, packetHandler, ADDR_PRO_GOAL_VELOCITY, LEN_PRO_GOAL_VELOCITY)
groupSyncReadVel = GroupSyncRead(portHandler, packetHandler, ADDR_PRO_PRESENT_VELOCITY, LEN_PRO_PRESENT_VELOCITY)

# Open port
if portHandler.openPort():
    print("Succeeded to open the port")
else:
    print("Failed to open the port. Exiting..")
    quit()

# Set port baudrate
if portHandler.setBaudRate(BAUDRATE):
    print("Succeeded to change the baudrate")
else:
    print("Failed to change the baudrate. Exiting..")
    quit()


# Setup for velocity controlled motors(ground vehicle)
for i in dxl_id_vel:
    # Disable Dynamixel#00i Torque Before operation mode change
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, i, ADDR_PRO_TORQUE_ENABLE, TORQUE_DISABLE)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
    else:
        print("Dynamixel#%d has been successfully connected" % i)

    # Change Dynamixel#00i operation mode
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, i, ADDR_PRO_OPERATING_MODE, VELOCITY_MODE)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
    else:
        print("Dynamixel#%d has been successfully connected" % i)

    # Enable Dynamixel#00i Torque
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, i, ADDR_PRO_TORQUE_ENABLE, TORQUE_ENABLE)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
    else:
        print("Dynamixel#%d has been successfully connected" % i)


command_idx=0
# Setup
for i in dxl_id_pos:
    print("before4")
    print("i:",i)
    print(ADDR_PRO_TORQUE_ENABLE)
    print(portHandler)
    # DISABLE Dynamixel#00i Torque
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, i, ADDR_PRO_TORQUE_ENABLE, TORQUE_DISABLE)
    print("before41")

    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
    else:
        print("Dynamixel#%d has been successfully connected" % i)

    print("before44")

    # Enable Dynamixel#00i Torque
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, i, ADDR_PRO_TORQUE_ENABLE, TORQUE_ENABLE)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
    else:
        print("Dynamixel#%d has been successfully connected" % i)

    # Set profile acceleration
    dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, i, ADDR_PRO_PROFILE_ACC, dxl_pos_control[str(i)]["profile"]["acc"])
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))

    # Set profile velocity
    dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, i, ADDR_PRO_PROFILE_VEL, dxl_pos_control[str(i)]["profile"]["vel"])
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
    
    # Add parameter storage for Dynamixel#00i present position value
    dxl_addparam_result = groupSyncReadPos.addParam(i)
    if dxl_addparam_result != True:
        print("[ID:%03d] groupSyncRead addparam failed" % i)
        quit()

print("before5")

def read_cmd(latest_idx):
    b_update = False
    try:
        with open(__filename_command__, "r") as file:
            dict = json.load(file)
        # latest_idx=dict["idx"]
    except:
        dict=[]
        print("read_cmd:json loading failed")
    else:
        if dict["idx"]>latest_idx or dict["idx"]==0:
            print(dict)
            latest_idx=dict["idx"]
            b_update = True
    return [b_update, latest_idx, dict]

def check_exit():
    # try:
    #     with open(__filename_flag__, "r") as file:
    #         dict = json.load(file)
    # except:
    #     dict=[]
    #     print("check_exit: json loading failed")
    # else:
    #     if dict["MODE"]!="NORMAL":
    #         print(dict)
    #         return True
    return False

def dxl_SyncWrite(h_groupSyncWrite,dxl_Ids,target_state):
    for id in dxl_Ids:
        i=str(id)
        # Allocate goal position value into byte array
        buffer = [DXL_LOBYTE(DXL_LOWORD(target_state[i])), DXL_HIBYTE(DXL_LOWORD(target_state[i])), DXL_LOBYTE(DXL_HIWORD(target_state[i])), DXL_HIBYTE(DXL_HIWORD(target_state[i]))]
        # Add Dynamixel#00i goal position value to the Syncwrite parameter storage
        dxl_addparam_result = h_groupSyncWrite.addParam(id, buffer)
        if dxl_addparam_result != True:
            print("[ID:%03d] groupSyncWrite addparam failed" % i)
            quit()
    # Syncwrite goal state
    print("goal:", target_state)
    dxl_comm_result = h_groupSyncWrite.txPacket()
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    # Clear syncwrite parameter storage
    h_groupSyncWrite.clearParam()

def dxl_ReadState(h_groupSyncRead,dxl_Ids,REG_ADDR,REG_LEN):
    # Syncread present state
    dxl_comm_result = h_groupSyncRead.txRxPacket()
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    dxl_current_state={}
    for i in dxl_Ids:
        # Check if groupsyncread data of Dynamixel#1 is available
        dxl_getdata_result = h_groupSyncRead.isAvailable(i, REG_ADDR, REG_LEN)
        if dxl_getdata_result != True:
            print("[ID:%03d] groupSyncRead getdata failed" % i)
            return [False, dxl_current_state]
        # Get Dynamixel#00i present state value
        dxl_current_state[str(i)]=h_groupSyncRead.getData(i, REG_ADDR, REG_LEN)
    return [True, dxl_current_state]

def print_state(dxl_target_pos):
    [isPosAvailable,dxl_current_pos]=dxl_ReadState(groupSyncReadPos,dxl_id_pos,ADDR_PRO_PRESENT_POSITION,LEN_PRO_PRESENT_POSITION)
    # [isvelAvailable,dxl_current_vel]=dxl_ReadState(groupSyncReadVel,dxl_id_gv,ADDR_PRO_PRESENT_VELOCITY,LEN_PRO_PRESENT_VELOCITY)
    # time.sleep(1)
    if isPosAvailable:
        isReached = True
        for id in dxl_id_pos:
            i=str(id)
            if (abs(dxl_current_pos[i]-dxl_target_pos[i])) > DXL_MOVING_STATUS_THRESHOLD:
                isReached = False
        if not isReached:
            print("current pos:",dxl_current_pos)

print("before11")

# Set to default state
dxl_goal_position=interp_maps(home_position,calib_map["pos"]["pos"],calib_map["pos"]["raw"],np.int32)
dxl_SyncWrite(groupSyncWritePos,dxl_id_pos,dxl_goal_position)


#main loop
while 1:
    #print_state(dxl_goal_position)    
    [b_newData,command_idx,cmd_obj]=read_cmd(command_idx)
    if b_newData == True:
        # update target-state
        print("update")
        print(cmd_obj)
        print("???")
        print(calib_map)
        dxl_goal_position=interp_maps(cmd_obj["pos"],calib_map["pos"]["pos"],calib_map["pos"]["raw"],np.int32)
        # dxl_goal_velocity=interp_maps(cmd_obj["vel"],calib_map["vel"]["vel"],calib_map["vel"]["raw"],np.int32)
        # write to dxl
        dxl_SyncWrite(groupSyncWritePos,dxl_id_pos,dxl_goal_position)
        # dxl_SyncWrite(groupSyncWriteVel,dxl_id_vel,dxl_goal_velocity)

    
    # if check_exit() == True:
    #     dxl_goal_position=interp_maps(home_position,calib_map["arm"]["pos"],calib_map["arm"]["raw"],np.int32)
    #     dxl_SyncWrite(groupSyncWritePos,dxl_id_arm,dxl_goal_position)
    #     time.sleep(5)
    #     break

for i in dxl_id_pos:
    # DISABLE Dynamixel#00i Torque
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, i, ADDR_PRO_TORQUE_ENABLE, TORQUE_DISABLE)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
# Close port
portHandler.closePort()
print("Motor torque disabled. Robot operation terminated.")
