#ref: https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python
import serial.tools.list_ports
import sys
import os
import json


# ports = serial.tools.list_ports.comports()
# for port, description, hwid in sorted(ports):
#         print("{}: {} [{}]".format(port, description, hwid))

# relative file path
if getattr(sys, 'frozen', False):
    __dirname__ =os.path.join(sys._MEIPASS,"..","..") # runned as a .exe file
else:
    __dirname__ =os.path.dirname(os.path.realpath(__file__)) # runned as a .py file

__filename_Comport__ = os.path.join(__dirname__,"src","config","Comport.txt")

class COMPorts:
    def __init__(self, data: list):
        self.data = data

    @classmethod
    def get_com_ports(cls):
        data = []
        ports = list(serial.tools.list_ports.comports())

        for port_ in ports:
            obj = Object(data=dict({"device": port_.device, "description": port_.description.split("(")[0].strip()}))
            data.append(obj)

        return cls(data=data)

    @staticmethod
    def get_description_by_device(device: str):
        for port_ in COMPorts.get_com_ports().data:
            if port_.device == device:
                return port_.description
        return None

    @staticmethod
    def get_device_by_description(description: str):
        for port_ in COMPorts.get_com_ports().data:
            if port_.description == description:
                return port_.device
        return None


class Object:
    def __init__(self, data: dict):
        self.data = data
        self.device = data.get("device")
        self.description = data.get("description")


if __name__ == "__main__":
    for port in COMPorts.get_com_ports().data:
        print("[{}]: {}".format(port.device, port.description))

    # print("Get device by description:"+COMPorts.get_device_by_description(description="USB-SERIAL CH340"))
    # print("Get description by port id:"+COMPorts.get_description_by_device(device="COM13"))

    ports = {}
    device = COMPorts.get_device_by_description(description="USB-SERIAL CH340")
    if not device==None:
        ports["dxlCh0"]={"port":device,"baudrate":"57600"}

    with open(__filename_Comport__, "w") as file:
        json.dump(ports, file, indent = 4)
        print("Saved the scanned comports:")
        print(ports)
