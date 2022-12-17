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

_availableRobotClass = ["robotArm","plantWatcher"]

if len(sys.argv) < 2 :
  print("INPUT ERROR: Input _robotClass")
  print("Example input:")
  print("* 'robotArm' -> full calibration[multi-step]")
  print("* 'robotArm home' -> home calibration[single-step]")
  print("Available robotClass ->")
  print(_availableRobotClass)
  quit()
elif not sys.argv[1] in _availableRobotClass:
  print("INPUT ERROR: Wrong input.")
  quit()

_robotClass = sys.argv[1]
_calibMode = sys.argv[2] if len(sys.argv) > 2 else "multi"


# relative file path
if getattr(sys, 'frozen', False):
    __dirname__ =os.path.join(sys._MEIPASS,"..","..") # runned as a .exe file
else:
    __dirname__ =os.path.dirname(os.path.realpath(__file__)) # runned as a .py file

__filename_calibration_dxl_arm__ = os.path.join(__dirname__,"src","calibration","dxl_arm.txt")
__filename_Comport__ = os.path.join(__dirname__,"src","config","Comport.txt")

# with open(os.path.join(__dirname__,"src","config","Comport.txt"), "r") as file:
#   config_comport=eval(file.readline())

with open(__filename_Comport__, "r") as file:
  config_comport=json.load(file)



# with open(os.path.join(__dirname__,"src","config","Comport.txt"), "r") as file:
#   config_comport=eval(file.readline())
# print("dxl_param reading success!")

# Comport Settings
BAUDRATE                 = config_comport['dxlCh0']['baudrate']  # Dynamixel default baudrate : 57600
COMPORT                  = config_comport['dxlCh0']['port']      # Check which port is being used on your controller
                                                                   # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"
BAUDRATE = 57600
COMPORT = "/dev/ttyUSB0"
# Initialize PortHandler&PacketHandler instance
portHandler = PortHandler(COMPORT)
packetHandler = PacketHandler(PROTOCOL_VERSION)
# Initialize GroupSync Read & Write instance
groupSyncWrite = GroupSyncWrite(portHandler, packetHandler, ADDR_PRO_GOAL_POSITION, LEN_PRO_GOAL_POSITION)
groupSyncRead = GroupSyncRead(portHandler, packetHandler, ADDR_PRO_PRESENT_POSITION, LEN_PRO_PRESENT_POSITION)

# Open port
if portHandler.openPort():
    print("Succeeded to open the port")
else:
    print("Failed to open the port")
    quit()

# Set port baudrate
if portHandler.setBaudRate(BAUDRATE):
    print("Succeeded to change the baudrate")
else:
    print("Failed to change the baudrate")
    quit()

def dxl_config(id_table):
  for i in id_table:
    # Disable Dynamixel#00i Torque
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, i, ADDR_PRO_TORQUE_ENABLE, TORQUE_DISABLE)
    if dxl_comm_result != COMM_SUCCESS:
        print("Dynamixel", i, ":", packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("Dynamixel", i, ":", packetHandler.getRxPacketError(dxl_error))
    else:
        print("Dynamixel#%d has been successfully connected" % i)
    
    # Add parameter storage for Dynamixel#00i present position value
    dxl_addparam_result = groupSyncRead.addParam(i)
    if dxl_addparam_result != True:
        print("[ID:%03d] groupSyncRead addparam failed" % i)
        exit()


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

calib_pos_dxl={}


def runCalibSteps(calib_guide, id_table):
  for idx, description in calib_guide.items():
    print("Set the robot to position ",idx, "- "+description)
    print("Ready? [y:proceed/n:exit]")
    while True:
      if _calibMode=="home":
        print("--> Auto-ready")
        ch= 'y'
      else:
        ch = getch()
        
      if ch =='y' or ch=='Y':
        calib_pos_dxl[idx]=get_dxl_position(id_table)
        print("current pos:",calib_pos_dxl)        
        break
      elif ch =='n' or ch=='N':
        exit()

##############################################################################
# Main

if _robotClass == "robotArm":
  calib_input_range={
    0:[-90, 90],
    1:[-90, 90],
    2:[-90,137],
    3:[-270,270],
    4:[-90, 90],
    5:[-270, 270],
    6:[  0, 90],
  }

  if _calibMode == "home":
    _calib_guide={
      0:"Home position & grip state",
    }
  else:
    _calib_guide={
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
elif _robotClass == "plantWatcher":
  calib_input_range={
    0:[ 0, 10*1000],
    1:[ -90, 90],
    2:[-180, 180],
    3:[-180, 180],
  }
  if _calibMode == "home":
    _calib_guide={
      0:"Home position (Dolly: ground level, Arm: straight)",
    }
  else:
    _calib_guide={
      0:"Home position (Dolly: ground level, Arm: straight)",
      1:"Arm: Motor 1 -90 degree (clockwise)",
      2:"Arm: Motor 1 +90 degree (counter clockwise)",
      3:"Arm: Motor 2 -180 degree (clockwise)",
      4:"Arm: Motor 2 +180 degree (counter clockwise)",
      5:"Arm: Motor 3 -180 degree (clockwise)",
      6:"Arm: Motor 3 +180 degree (counter clockwise)",
      7:"Dolly: 1.0 m from ground level",
    }

dxl_id_table = list(calib_input_range.keys())
dxl_config(dxl_id_table)
runCalibSteps(_calib_guide, dxl_id_table)
# calib_map=setCalibMap(_calibMode, calib_input_range)


range_map={"pos":{}, "raw":{}}
for idx, val in calib_input_range.items():
  range_map["pos"][idx]=val
if _robotClass == "robotArm":
  if _calibMode == "home":
    idx=0
    range_map["raw"][idx]=[calib_pos_dxl[0][idx]-2200,calib_pos_dxl[0][idx]+2200]
    idx=1
    range_map["raw"][idx]=[calib_pos_dxl[0][idx],calib_pos_dxl[0][idx]+2810]
    idx=2
    range_map["raw"][idx]=[calib_pos_dxl[0][idx]+3500,calib_pos_dxl[0][idx]]
    idx=3
    range_map["raw"][idx]=[calib_pos_dxl[0][idx]-3072,calib_pos_dxl[0][idx]+3072]
    idx=4
    range_map["raw"][idx]=[calib_pos_dxl[0][idx]+1023,calib_pos_dxl[0][idx]-1023]
    idx=5
    range_map["raw"][idx]=[calib_pos_dxl[0][idx]-3072,calib_pos_dxl[0][idx]+3072]
    idx=6
    range_map["raw"][idx]=[calib_pos_dxl[0][idx]-880,calib_pos_dxl[0][idx]]
  else:
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
elif _robotClass == "plantWatcher":
  if _calibMode == "home":
    idx=0
    range_map["raw"][idx]=[calib_pos_dxl[0][idx],calib_pos_dxl[0][idx]+10*20000]
    idx=1
    range_map["raw"][idx]=[calib_pos_dxl[0][idx]-1024,calib_pos_dxl[0][idx]+1024]
    idx=2
    range_map["raw"][idx]=[calib_pos_dxl[0][idx]-2048,calib_pos_dxl[0][idx]+2048]
    idx=3
    range_map["raw"][idx]=[calib_pos_dxl[0][idx]-2048,calib_pos_dxl[0][idx]+2048]
  else : # need verification
    idx=0
    range_map["raw"][idx]=[calib_pos_dxl[0][idx],calib_pos_dxl[0][idx]+10*(calib_pos_dxl[7][idx]-calib_pos_dxl[0][idx])]
    idx=1
    range_map["raw"][idx]=[calib_pos_dxl[1][idx],calib_pos_dxl[2][idx]]
    idx=2
    range_map["raw"][idx]=[calib_pos_dxl[3][idx],calib_pos_dxl[4][idx]]
    idx=3
    range_map["raw"][idx]=[calib_pos_dxl[5][idx],calib_pos_dxl[6][idx]]

print("Calibration procedure finished.")
calib_map = range_map

with open(__filename_calibration_dxl_arm__, "w") as file:
  json.dump(calib_map,file,indent=4)
  # file.write(str(calib_map))
print("EXIT: calibration success!")
    
# Close port
portHandler.closePort()
