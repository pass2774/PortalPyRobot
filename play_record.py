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
from time import time, sleep
import cmd_manager
import sys

# relative file path
if getattr(sys, 'frozen', False):
    __dirname__ =os.path.join(sys._MEIPASS,"..","..") # runned as a .exe file
else:
    __dirname__ =os.path.dirname(os.path.realpath(__file__)) # runned as a .py file

__filename_log_command__ = os.path.join(__dirname__,"log_command.txt")
# __filename_log_command__ = os.path.join(__dirname__,"log_command_example.txt")

with open(__filename_log_command__, "r") as file:
    log_command = json.load(file)

while True:
    start_time= time()
    print("starting time:", start_time-time())
    # command=log_command[0]["data"]
    # try:
    #     cmd_manager.update_commandFile(command)
    # except:
    #     pass    
    sleep(5)
    for queue in log_command:
        t0=queue["t0"]
        dt=t0+start_time-time()
        if dt>0:
            sleep(dt)
        command=queue["data"]
        print("time:",t0,"command:",command)
        try:
            cmd_manager.update_commandFile(command)
        except:
            pass


