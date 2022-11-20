import signal
import time


print("test.py started")

def signal_handler(signum, frame):
    print("signal number:",signum," Frame:",frame)
    print("The loop--test.py-- is exited")
    exit(0)

signal.signal(signal.SIGINT, signal_handler)

while True:
    print("test.py-time:")
    print(time.time())
    time.sleep(1)
