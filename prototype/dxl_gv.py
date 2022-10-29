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
import time
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

# Protocol version
PROTOCOL_VERSION            = 2.0               # See which protocol version is used in the Dynamixel
# Control table address
ADDR_PRO_TORQUE_ENABLE      = 64               # Control table address is different in Dynamixel model
ADDR_PRO_GOAL_POSITION      = 116
ADDR_PRO_GOAL_VELOCITY      = 104
ADDR_PRO_PRESENT_POSITION   = 132
ADDR_PRO_PRESENT_VELOCITY   = 128
ADDR_PRO_PROFILE_ACC        = 108
ADDR_PRO_PROFILE_VEL        = 112
ADDR_PRO_OPERATING_MODE     = 11
# Data Byte Length
LEN_PRO_GOAL_POSITION       = 4
LEN_PRO_GOAL_VELOCITY       = 4
LEN_PRO_PRESENT_POSITION    = 4
LEN_PRO_PRESENT_VELOCITY    = 4
# Data definition
TORQUE_ENABLE               = 1                 # Value for enabling the torque
TORQUE_DISABLE              = 0                 # Value for disabling the torque
DXL_MOVING_STATUS_THRESHOLD = 20                # Dynamixel moving status threshold

VELOCITY_MODE               = 1
POSITION_MODE               = 3
EXTENDED_POSITITON_MODE     = 4
PWM_MODE                    = 16

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
__dirname__ =os.path.dirname(os.path.realpath(__file__))
calib_map={}
with open(os.path.join(__dirname__,"calibration","dxl_arm.txt"), "r") as file:
  calib_map["arm"]=eval(file.readline())
with open(os.path.join(__dirname__,"calibration","dxl_gv.txt"), "r") as file:
  calib_map["gv"]=eval(file.readline())
print("calibration map reading done!")

# dxl_default_angle = {0:0,1:-50,2:130,3:0,4:0,5:0}
dxl_goal_angle = dxl_param["home-position"]
dxl_goal_position={}

# dxl_id_table =[0,1,2,3,4,5,6]
dxl_id_table =[]
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


velmap={
    'vel': {21: [-100, 100], 22: [-100, 100], 23: [-100, 100], 24: [-100, 100]},
    'raw': {21: [-265, 265], 22: [265, -265], 23: [-265, 265], 24: [265, -265]},
}
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
    dxl_addparam_result = groupSyncReadPos.addParam(i)
    if dxl_addparam_result != True:
        print("[ID:%03d] groupSyncRead addparam failed" % i)
        quit()


    dxl_goal_position=interp_maps(dxl_goal_angle,calib_map["arm"]["angle"],calib_map["arm"]["raw"],np.int32)
    # Set initial goal position
    for i in dxl_id_table:

        # Allocate goal position value into byte array
        param_goal_position = [DXL_LOBYTE(DXL_LOWORD(dxl_goal_position[i])), DXL_HIBYTE(DXL_LOWORD(dxl_goal_position[i])), DXL_LOBYTE(DXL_HIWORD(dxl_goal_position[i])), DXL_HIBYTE(DXL_HIWORD(dxl_goal_position[i]))]
        
        # Add Dynamixel#00i goal position value to the Syncwrite parameter storage
        dxl_addparam_result = groupSyncWritePos.addParam(i, param_goal_position)
        if dxl_addparam_result != True:
            print("[ID:%03d] groupSyncWrite addparam failed" % i)
            quit()

    # Syncwrite goal position
    print("goal:", dxl_goal_position)
    dxl_comm_result = groupSyncWritePos.txPacket()
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))

    # Clear syncwrite parameter storage
    groupSyncWritePos.clearParam()

#main loop
while 1:
    # Syncread present position
    dxl_comm_result = groupSyncReadPos.txRxPacket()
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))

    dxl_present_position={}
    isReached = True

    for i in dxl_id_table:
        # Check if groupsyncread data of Dynamixel#1 is available
        dxl_getdata_result = groupSyncReadPos.isAvailable(i, ADDR_PRO_PRESENT_POSITION, LEN_PRO_PRESENT_POSITION)
        if dxl_getdata_result != True:
            print("[ID:%03d] groupSyncRead getdata failed" % i)
            # quit()
        # Get Dynamixel#00i present position value
        dxl_present_position[i]=groupSyncReadPos.getData(i, ADDR_PRO_PRESENT_POSITION, LEN_PRO_PRESENT_POSITION)
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
                # dxl_goal_velocity = dict["gv"]
    
    b_newData = True
    if b_newData == True:
        # Change goal position
        dxl_goal_position=interp_maps(dxl_goal_angle,calib_map["arm"]["angle"],calib_map["arm"]["raw"],np.int32)
                        
        for i in dxl_id_table:
            # Allocate goal position value into byte array
            param_goal_position = [DXL_LOBYTE(DXL_LOWORD(dxl_goal_position[i])), DXL_HIBYTE(DXL_LOWORD(dxl_goal_position[i])), DXL_LOBYTE(DXL_HIWORD(dxl_goal_position[i])), DXL_HIBYTE(DXL_HIWORD(dxl_goal_position[i]))]
            
            # Add Dynamixel#00i goal position value to the Syncwrite parameter storage
            dxl_addparam_result = groupSyncWritePos.addParam(i, param_goal_position)
            if dxl_addparam_result != True:
                print("[ID:%03d] groupSyncWrite addparam failed" % i)
                quit()

        # Syncwrite goal position
        print("goal:", dxl_goal_position)
        dxl_comm_result = groupSyncWritePos.txPacket()
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))

        # Clear syncwrite parameter storage
        groupSyncWritePos.clearParam()


        dxl_goal_velocity_raw = {21:0,22:0,23:0,24:0}
        # dxl_goal_velocity_raw = {21:10,22:10,23:10,24:10}
        # dxl_goal_velocity=interp_maps(dxl_goal_velocity_raw,velmap["vel"],velmap["raw"],np.int32)
        dxl_goal_velocity=interp_maps(dxl_goal_velocity_raw,calib_map["gv"]["vel"],calib_map["gv"]["raw"],np.int32)

        for i in dxl_id_gv:
            # Allocate goal position value into byte array
            param_goal_velocity = [DXL_LOBYTE(DXL_LOWORD(dxl_goal_velocity[i])), DXL_HIBYTE(DXL_LOWORD(dxl_goal_velocity[i])), DXL_LOBYTE(DXL_HIWORD(dxl_goal_velocity[i])), DXL_HIBYTE(DXL_HIWORD(dxl_goal_velocity[i]))]
            
            # Add Dynamixel#00i goal position value to the Syncwrite parameter storage
            dxl_addparam_result = groupSyncWriteVel.addParam(i, param_goal_velocity)
            if dxl_addparam_result != True:
                print("[ID:%03d] groupSyncWrite addparam failed" % i)
                quit()

        time.sleep(1)
        # Syncwrite goal state
        print("goal:", dxl_goal_velocity)
        dxl_comm_result = groupSyncWriteVel.txPacket()
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))

        # Clear syncwrite parameter storage
        groupSyncWriteVel.clearParam()

# Clear syncread parameter storage
# groupSyncReadPos.clearParam()

# for i in dxl_id_table:
#     # Disable Dynamixel#00i Torque
#     dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, i, ADDR_PRO_TORQUE_ENABLE, TORQUE_DISABLE)
#     if dxl_comm_result != COMM_SUCCESS:
#         print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
#     elif dxl_error != 0:
#         print("%s" % packetHandler.getRxPacketError(dxl_error))
    
# Close port
portHandler.closePort()
