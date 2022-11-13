#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
# Copyright 2017 ROBOTIS CO., LTD.
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
from pickle import FALSE
import numpy as np
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


with open("config_comport.txt", "r") as file:
  config_comport=eval(file.readline())
print("dxl_param reading success!")

# Comport Settings
BAUDRATE                 = config_comport['RobotArm']['baudrate']  # Dynamixel default baudrate : 57600
COMPORT                  = config_comport['RobotArm']['port']      # Check which port is being used on your controller
                                                                   # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"

with open("dxl_param.txt", "r") as file:
  dxl_param=eval(file.readline())
print("dxl_param reading success!")
    

def interp_maps(x,map_x,map_y,dtype):
  y={}
  for idx, value in x.items():
    if map_x[idx][1]>=map_x[idx][0]:
      y[idx]=np.interp(value,map_x[idx],map_y[idx]).astype(dtype)
    else:
      y[idx]=np.interp(-value,[-map_x[idx][0],-map_x[idx][1]],map_y[idx]).astype(dtype)
  return y

#read the calibration map data
calib_map={}
with open("dxl_calibration.txt", "r") as file:
  calib_map=eval(file.readline())
print("map reading success!")

# dxl_default_angle = {0:0,1:-50,2:130,3:0,4:0,5:0}
dxl_goal_angle = dxl_param["home-position"]
dxl_goal_position={}

dxl_id_table =[0,1,2,3,4,5,6]

# Initialize PortHandler instance - Set the port path
portHandler = PortHandler(COMPORT)
# Initialize PacketHandler instance - Set the protocol version
packetHandler = PacketHandler(PROTOCOL_VERSION)
# Initialize GroupSync Read & Write instance
groupSyncWrite = GroupSyncWrite(portHandler, packetHandler, ADDR_PRO_GOAL_POSITION, LEN_PRO_GOAL_POSITION)
groupSyncRead = GroupSyncRead(portHandler, packetHandler, ADDR_PRO_PRESENT_POSITION, LEN_PRO_PRESENT_POSITION)

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

command_idx=0
# Setup
for i in dxl_id_table:
    # Enable Dynamixel#00i Torque
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, i, ADDR_PRO_TORQUE_ENABLE, TORQUE_ENABLE)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
    else:
        print("Dynamixel#%d has been successfully connected" % i)

    # Set profile acceleration
    dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, i, ADDR_PRO_PROFILE_ACC, dxl_param["profile"]["acc"][i])
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))

    # Set profile velocity
    dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, i, ADDR_PRO_PROFILE_VEL, dxl_param["profile"]["vel"][i])
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
    
    # Add parameter storage for Dynamixel#00i present position value
    dxl_addparam_result = groupSyncRead.addParam(i)
    if dxl_addparam_result != True:
        print("[ID:%03d] groupSyncRead addparam failed" % i)
        quit()


    dxl_goal_position=interp_maps(dxl_goal_angle,calib_map["angle"],calib_map["raw"],np.int32)
    # Set initial goal position
    for i in dxl_id_table:

        # Allocate goal position value into byte array
        param_goal_position = [DXL_LOBYTE(DXL_LOWORD(dxl_goal_position[i])), DXL_HIBYTE(DXL_LOWORD(dxl_goal_position[i])), DXL_LOBYTE(DXL_HIWORD(dxl_goal_position[i])), DXL_HIBYTE(DXL_HIWORD(dxl_goal_position[i]))]
        
        # Add Dynamixel#00i goal position value to the Syncwrite parameter storage
        dxl_addparam_result = groupSyncWrite.addParam(i, param_goal_position)
        if dxl_addparam_result != True:
            print("[ID:%03d] groupSyncWrite addparam failed" % i)
            quit()

    # Syncwrite goal position
    print("goal:", dxl_goal_position)
    dxl_comm_result = groupSyncWrite.txPacket()
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))

    # Clear syncwrite parameter storage
    groupSyncWrite.clearParam()

#main loop
while 1:
    # Syncread present position
    dxl_comm_result = groupSyncRead.txRxPacket()
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))

    dxl_present_position={}
    isReached = True
    for i in dxl_id_table:
        # Check if groupsyncread data of Dynamixel#1 is available
        dxl_getdata_result = groupSyncRead.isAvailable(i, ADDR_PRO_PRESENT_POSITION, LEN_PRO_PRESENT_POSITION)
        if dxl_getdata_result != True:
            print("[ID:%03d] groupSyncRead getdata failed" % i)
            # quit()
        # Get Dynamixel#00i present position value
        dxl_present_position[i]=groupSyncRead.getData(i, ADDR_PRO_PRESENT_POSITION, LEN_PRO_PRESENT_POSITION)
        # print("[ID:%03d] GoalPos:%03d PresPos:%03d\t" % (i, dxl_position_range[i][index], dxl_present_position[i]))
        if (abs(dxl_present_position[i]-dxl_goal_position[i])) > DXL_MOVING_STATUS_THRESHOLD:
            isReached = False
    if not isReached:
        print(dxl_present_position)
    
    file = open("output.txt", "r")
    b_newData = False
    while True:
        try:
            line = file.readline()
            if not line:
                break
            dict=eval(line)

        except:
            print("eval() error!")

        else:
            if dict["idx"]>command_idx:
                print(line)
                command_idx=dict["idx"]
                b_newData = True
                dxl_goal_angle = dict["arm"]
                gimbal_goal_position = dict["gimbal"]

    
    if b_newData == True:
        # Change goal position
        dxl_goal_position=interp_maps(dxl_goal_angle,calib_map["angle"],calib_map["raw"],np.int32)
                        
        for i in dxl_id_table:
            # Allocate goal position value into byte array
            param_goal_position = [DXL_LOBYTE(DXL_LOWORD(dxl_goal_position[i])), DXL_HIBYTE(DXL_LOWORD(dxl_goal_position[i])), DXL_LOBYTE(DXL_HIWORD(dxl_goal_position[i])), DXL_HIBYTE(DXL_HIWORD(dxl_goal_position[i]))]
            
            # Add Dynamixel#00i goal position value to the Syncwrite parameter storage
            dxl_addparam_result = groupSyncWrite.addParam(i, param_goal_position)
            if dxl_addparam_result != True:
                print("[ID:%03d] groupSyncWrite addparam failed" % i)
                quit()

        # Syncwrite goal position
        print("goal:", dxl_goal_position)
        dxl_comm_result = groupSyncWrite.txPacket()
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))

        # Clear syncwrite parameter storage
        groupSyncWrite.clearParam()

# Clear syncread parameter storage
groupSyncRead.clearParam()

for i in dxl_id_table:
    # Disable Dynamixel#00i Torque
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, i, ADDR_PRO_TORQUE_ENABLE, TORQUE_DISABLE)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
    
# Close port
portHandler.closePort()
