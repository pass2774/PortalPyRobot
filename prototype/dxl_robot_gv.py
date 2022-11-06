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

import os
import json
from pickle import FALSE
import numpy as np
import time
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
# relative file path
__dirname__ =os.path.dirname(os.path.realpath(__file__))
__filename_command__ = os.path.join(__dirname__,"command.txt")

with open(os.path.join(__dirname__,"config_comport.txt"), "r") as file:
  config_comport=eval(file.readline())
print("dxl_param reading success!")

# Comport Settings
BAUDRATE                 = config_comport['RobotArm']['baudrate']  # Dynamixel default baudrate : 57600
COMPORT                  = config_comport['RobotArm']['port']      # Check which port is being used on your controller
                                                                   # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"

with open(os.path.join(__dirname__,"calibration","dxl_param.txt"), "r") as file:
  dxl_param=json.load(file)
print("dxl_param reading success!")
    

def interp_maps(x,map_x,map_y,dtype):
  y={}
  for idx, value in x.items():
    if map_x[idx][1]>=map_x[idx][0]:
      y[idx]=np.interp(value,map_x[idx],map_y[idx]).astype(dtype)
    else:
      y[idx]=np.interp(-value,[-map_x[idx][0],-map_x[idx][1]],map_y[idx]).astype(dtype)
  return y

calib_map={}
#read the calibration map data
with open(os.path.join(__dirname__,"calibration","dxl_arm.txt"), "r") as file:
  calib_map["arm"]=json.load(file)
#   calib_map["arm"]=eval(file.readline())
with open(os.path.join(__dirname__,"calibration","dxl_gv.txt"), "r") as file:
  calib_map["gv"]=json.load(file)
#   calib_map["gv"]=eval(file.readline())
print("calibration map reading done!")

# dxl_default_angle = {0:0,1:-50,2:130,3:0,4:0,5:0}
dxl_goal_arm = dxl_param["home-position"]
dxl_goal_position={}

dxl_id_arm =[0,1,2,3,4,5,6]
# dxl_id_arm =[]
dxl_id_gv =[21,22,23,24]

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
    print("Failed to open the port")
    print("Press any key to terminate...")
    getch()
    quit()

# Set port baudrate
if portHandler.setBaudRate(BAUDRATE):
    print("Succeeded to change the baudrate")
else:
    print("Failed to change the baudrate")
    print("Press any key to terminate...")
    getch()
    quit()


# Setup for gv(ground vehicle)
for i in dxl_id_gv:
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
for i in dxl_id_arm:
    # DISABLE Dynamixel#00i Torque
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, i, ADDR_PRO_TORQUE_ENABLE, TORQUE_DISABLE)
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

    # Set profile acceleration
    dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, i, ADDR_PRO_PROFILE_ACC, dxl_param["profile"]["acc"][str(i)])
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))

    # Set profile velocity
    dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, i, ADDR_PRO_PROFILE_VEL, dxl_param["profile"]["vel"][str(i)])
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
    
    # Add parameter storage for Dynamixel#00i present position value
    dxl_addparam_result = groupSyncReadPos.addParam(i)
    if dxl_addparam_result != True:
        print("[ID:%03d] groupSyncRead addparam failed" % i)
        quit()

def read_cmd(latest_idx):
    with open(__filename_command__, "r") as file:
        dict = json.load(file)
    # latest_idx=dict["idx"]
    if dict["idx"]>latest_idx or dict["idx"]==0:
        print(dict)
        latest_idx=dict["idx"]
        b_update = True
    else:
        b_update = False
    return [b_update, latest_idx, dict]

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
    [isPosAvailable,dxl_current_pos]=dxl_ReadState(groupSyncReadPos,dxl_id_arm,ADDR_PRO_PRESENT_POSITION,LEN_PRO_PRESENT_POSITION)
    # [isvelAvailable,dxl_current_vel]=dxl_ReadState(groupSyncReadVel,dxl_id_gv,ADDR_PRO_PRESENT_VELOCITY,LEN_PRO_PRESENT_VELOCITY)
    # time.sleep(1)
    if isPosAvailable:
        isReached = True
        for id in dxl_id_arm:
            i=str(id)
            if (abs(dxl_current_pos[i]-dxl_target_pos[i])) > DXL_MOVING_STATUS_THRESHOLD:
                isReached = False
        if not isReached:
            print("current pos:",dxl_current_pos)

# Set to default state
dxl_goal_position=interp_maps(dxl_goal_arm,calib_map["arm"]["angle"],calib_map["arm"]["raw"],np.int32)
dxl_SyncWrite(groupSyncWritePos,dxl_id_arm,dxl_goal_position)

#main loop
while 1:
    print_state(dxl_goal_position)    
    [b_newData,command_idx,cmd_obj]=read_cmd(command_idx)
    if b_newData == True:
        # update target-state
        dxl_goal_position=interp_maps(cmd_obj["arm"],calib_map["arm"]["angle"],calib_map["arm"]["raw"],np.int32)
        dxl_goal_velocity=interp_maps(cmd_obj["gv"],calib_map["gv"]["vel"],calib_map["gv"]["raw"],np.int32)
        # write to dxl
        dxl_SyncWrite(groupSyncWritePos,dxl_id_arm,dxl_goal_position)
        dxl_SyncWrite(groupSyncWriteVel,dxl_id_gv,dxl_goal_velocity)

# Clear syncread parameter storage
groupSyncReadPos.clearParam()

for i in dxl_id_arm:
    # Disable Dynamixel#00i Torque
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, i, ADDR_PRO_TORQUE_ENABLE, TORQUE_DISABLE)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
    
# Close port
portHandler.closePort()
