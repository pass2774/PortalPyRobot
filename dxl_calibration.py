#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
# Copyright 2022 PORTAL301 CO., LTD.
# Author: Joonhwa Choi
# To calibrate the dynamixel motors and get the operatable zone of the robot arm

################################################################################


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

# relative file path
__dirname__ =os.path.dirname(os.path.realpath(__file__))
__filename_calibration_dxl_arm__ = os.path.join(__dirname__,"src","calibration","dxl_arm.txt")

# with open("config_comport.txt", "r") as file:
with open(os.path.join(__dirname__,"src","config","Comport.txt"), "r") as file:
  config_comport=eval(file.readline())
print("dxl_param reading success!")

# Comport Settings
BAUDRATE                 = config_comport['RobotArm']['baudrate']  # Dynamixel default baudrate : 57600
COMPORT                  = config_comport['RobotArm']['port']      # Check which port is being used on your controller
                                                                   # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"

def interp_maps(x,map_x,map_y,dtype):
  y={}
  for idx, value in x.items():
    if map_x[idx][1]>=map_x[idx][0]:
      y[idx]=np.interp(value,map_x[idx],map_y[idx]).astype(dtype)
    else:
      y[idx]=np.interp(-value,[-map_x[idx][0],-map_x[idx][1]],map_y[idx]).astype(dtype)
  return y


dxl_id_table =[0,1,2,3,4,5,6]

# Initialize PortHandler instance
portHandler = PortHandler(COMPORT)

# Initialize PacketHandler instance
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
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, i, ADDR_PRO_TORQUE_ENABLE, TORQUE_DISABLE)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
    else:
        print("Dynamixel#%d has been successfully connected" % i)
    
    # Add parameter storage for Dynamixel#00i present position value
    dxl_addparam_result = groupSyncRead.addParam(i)
    if dxl_addparam_result != True:
        print("[ID:%03d] groupSyncRead addparam failed" % i)
        quit()

def get_dxl_position(id_table):
  # Syncread present position
  dxl_comm_result = groupSyncRead.txRxPacket()
  if dxl_comm_result != COMM_SUCCESS:
      print("%s" % packetHandler.getTxRxResult(dxl_comm_result))

  pos={}
  for i in id_table:
      # Check if groupsyncread data of Dynamixel#1 is available
      dxl_getdata_result = groupSyncRead.isAvailable(i, ADDR_PRO_PRESENT_POSITION, LEN_PRO_PRESENT_POSITION)
      if dxl_getdata_result != True:
          print("[ID:%03d] groupSyncRead getdata failed" % i)
          # quit()
      # Get Dynamixel#00i present position value
      pos[i]=np.asarray(groupSyncRead.getData(i, ADDR_PRO_PRESENT_POSITION, LEN_PRO_PRESENT_POSITION)).astype(np.int32).item()
  return pos

calib_guide={
  0:"Home position",
  1:"Arm: straight veritcal",
  2:"Arm: reversed right angle & End-effecter: straight",
  3:"Arm: reversed right angle & End-effecter: backward right angle(adjust M4)",
  4:"Arm: reversed right angle & End-effecter: forward right angle(adjust M4)",
  5:"Arm: reversed right angle & End-effecter: 180 deg leftward(adjust M3)",
  6:"Arm: reversed right angle & End-effecter: 180 deg rightward(adjust M3)",
  7:"Arm: reversed right angle & End-effecter: 270 deg leftward rolling(adjust M5)",
  8:"Arm: reversed right angle & End-effecter: 270 deg rightward rolling(adjust M5)",
  9:"End-effecter: grip-state",
  10:"End-effecter: release-state",
}

calib_pos_dxl={}
def get_calib_pos():
  for idx, description in calib_guide.items():
    print("Set the robot to position ",idx, "- "+description)
    print("Ready? [y:proceed/n:exit]")
    while True:
      ch = getch()
      if ch =='y' or ch=='Y':
        calib_pos_dxl[idx]=get_dxl_position(dxl_id_table)
        print("current pos:",calib_pos_dxl)        
        break
      elif ch =='n' or ch=='N':
        exit()
    
calib_pos_angle={
  0:[-90, 90],
  1:[-90, 90],
  2:[-90,137],
  3:[-270,270],
  4:[-90, 90],
  5:[-270, 270],
  6:[  0, 90],
}

def setCalibMap():
  range_map={"angle":{}, "raw":{}}
  for idx, val in calib_pos_angle.items():
    range_map["angle"][idx]=val

  idx=0
  range_map["raw"][idx]=[calib_pos_dxl[0][idx]-2200,calib_pos_dxl[0][idx]+2200]
  idx=1
  range_map["raw"][idx]=[calib_pos_dxl[0][idx],calib_pos_dxl[2][idx]]
  idx=2
  range_map["raw"][idx]=[calib_pos_dxl[2][idx],calib_pos_dxl[0][idx]]
  idx=3
  range_map["raw"][idx]=[calib_pos_dxl[6][idx],calib_pos_dxl[5][idx]]
  idx=4
  range_map["raw"][idx]=[calib_pos_dxl[3][idx],calib_pos_dxl[4][idx]]
  idx=5
  range_map["raw"][idx]=[calib_pos_dxl[7][idx],calib_pos_dxl[8][idx]]
  idx=6
  range_map["raw"][idx]=[calib_pos_dxl[10][idx],calib_pos_dxl[9][idx]]

  return range_map

get_calib_pos()
print("Calibration successfully finished.")
calib_map=setCalibMap()

with open(__filename_calibration_dxl_arm__, "w") as file:
  json.dump(calib_map,file,indent=4)
  # file.write(str(calib_map))
print("success!")
    
# Close port
portHandler.closePort()
