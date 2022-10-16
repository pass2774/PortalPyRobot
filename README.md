## References
- Poetry: https://blog.gyus.me/2020/introduce-poetry/

- Dynamixel: http://emanual.robotis.com/docs/en/software/dynamixel/dynamixel_sdk/overview/

- Markdown for github README.md


## Setup Poetry module for package management
### 0-1. Installing poetry 
* Method1: for Linux
    ```
    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
    ```
* Method2: using pip(Raspberry PI)
    ```
    pip install --user poetry
    ```
-> 
The path for 'poetry commands' is supposed to be automatically added to 'environment variable'. 
If it does not work, you can use the poetry without adding 'poetry command' path to the environment variable.
In the console, input: 
source $HOME/.poetry/env

### 0-2. Frequently used poetry commands
        poetry init
        poetry update
        poetry install
        poetry add package_name(poetry add numpy)
        poetry run python filename.py

* For package management, you have to install packages via poetry.

## Description for main components
Three programs(command_socket.py, storm32.py, dynamixel_sync.py) operate independently.

1. prototype/command_socket.py --> for socket communication
It gets command data in JSON format from socket and save it in "output.txt" file.

2. prototype/storm32.py --> for gimbal
It reads command data for "gimbal" from "output.txt" file and control the gimbal by "serial communication".
Accordingly, you have to specify the serial port(ex. COM1 for windows or usb/tty0 for linux) of the gimbal in the code.

3. prototype/dxl_robot.py --> for robot with 6 motors
It reads command data for "arm" from "output.txt" file and control the motors by "serial communication".
In the same manner, you have to specify the serial port.


## Recommanded test procedure.
1-1. Run only 'command_socket.py' and check if "output.txt" changes.


2-1. Power on the gimbal & connect it to computer with a 'usb mini' cable. 
2-2. Before running 'storm32.py', run 'command_manual.py' once.
     in the 'command_manual.py', 

     (around line 80~90)
     arm = '{0:%d,1:%d,2:%d,3:%d,4:%d,5:%d}' % (4000,1000,900,600,1300,2300)
     gimbal = '{0:%d,1:%d,2:%d}' % (0,0,0)

     the line starting with 'gimbal' sets the angle of gimbal motor.
     The base angle is (roll,pitch,yaw) = (0,0,0) and you may change each value from -20~20 (actual range is wider, but it is practice step now).

     check if the data in "output.txt" file is in the form of:
     {"idx":000,"arm":{0:0000,1:0000,2:0000,3:0000,4:0000,5:0000},"gimbal":{0:0,1:0,2:0}}

2-3. Edit the line designating serial port of the storm32 in 'storm32.py'.
2-4. Run 'storm32.py'
2-5. if the gimbal normally works, then let's check if the angle of the gimbal can be changed.
     
     In 'command_manual.py', edit the line for gimbal angle.

    (around line 80~90)
    * From:
     gimbal = '{0:%d,1:%d,2:%d}' % (0,0,0)

    * To:
     gimbal = '{0:%d,1:%d,2:%d}' % (10,0,-10)

    save the file and run once. Then the gimbal would change its position.

2-6. Okay, now let's use 'command_socket.py' instead of 'command_manual.py'.
2-7. Transmit the command through the socket(Dr.YS will do it.)

*3-0. poetry run python prototype/setup_dynamixel.py install

*3-0. 'dynamixel_sync.py' --> I am busy and it is a little bit dangerour. Let's do it on Wednesday.

(Below is under construction)


3-1. run 'setup_dynamixel.py' it will install SDK for the dynamixel(dynamixel_sdk).