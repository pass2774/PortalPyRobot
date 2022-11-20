import subprocess
import platform
import time
import signal
import os
import json
import time

print(platform.system())
print(platform.release())
print(platform.version())

process_init=subprocess.Popen(['dist/init_profile/init_profile.exe'])
process_init.wait()
print("portal301 service profile initated")

# subprocess.Popen(['dist/cmd_socket/cmd_socket.exe'])
p_test=subprocess.Popen(['python','test.py'])
flag = False
def signal_handler(signum, frame):
    print("signal number:",signum," Frame:",frame)
    print("signal.sigint sending")
    p_test.send_signal(signal.CTRL_C_EVENT)
    # p_test.kill()
    print("signal.sigint sended")

    time.sleep(1)
    exit(0)

# relative file path
__dirname__ =os.path.dirname(os.path.realpath(__file__))
__filename_command__ = os.path.join(__dirname__,"command.txt")
__filename_flag__ = os.path.join(__dirname__,"flag.txt")

def check_exit():
    try:
        with open(__filename_flag__, "r") as file:
            dict = json.load(file)
    except:
        dict=[]
        print("json loading failed")
    else:
        if dict["MODE"]!="NORMAL":
            print(dict)
            return True
    return False





while True:
    time.sleep(1)
    mode = check_exit()
    if mode == "NORMAL":
        try:
            p_test.wait(timeout=10)
        except subprocess.TimeoutExpired:
            p_test.kill()
            p_test.wait()
        
    print("time:")
    print(time.time())
    if flag==True:
        break


