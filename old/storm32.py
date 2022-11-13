import time, os, sys, math
import serial
from STorM32_lib import *


# uart = "COM10"
uart = "/dev/ttyACM0"
baud = 115200

display = True
#display = False

if len(sys.argv) > 1:
    print(sys.argv[1])
    if sys.argv[1] == '57' or sys.argv[1] == '57600':
        baud = 57600
    if sys.argv[1] == '115' or sys.argv[1] == '115200':
        baud = 115200
        print('baudrate=')
        print(baud)
    if sys.argv[1] == '921' or sys.argv[1] == '921600':
        baud = 921600


ser = serial.Serial(uart, baud) 
t1Hz_last = time.perf_counter()

pitch = 0.0
pitch_dir = 1.0
yaw = 0.0
yaw_dir = 1.0

command_idx=0
while True:
    file = open("output.txt", "r")
    b_newData = False
    while True:
        try:
            line = file.readline()
            if not line:
                break
            dict=eval(line)
            if dict["idx"]>command_idx:
                print(line)
                command_idx=dict["idx"]
                b_newData = True
                dxl_goal_position = dict["arm"]
                gimbal_goal_position = dict["gimbal"]
        except:
            pass
        else:
            pass
        
    if b_newData == True:
        pitch = gimbal_goal_position[0]
        roll = gimbal_goal_position[1]
        yaw = gimbal_goal_position[2]
        cmd = cCMD_SETANGLES(ser,pitch,roll,yaw,False) # pitch, roll, yaw
        cmd.send()
        # Syncwrite goal position

    tnow = time.perf_counter()
    if tnow - t1Hz_last > 0.01:
        t1Hz_last += 0.01
        available = ser.in_waiting
        if available > 0:
            c = ser.read(available)
            print("<- ", c)
