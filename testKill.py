#!/usr/bin/env python3

import signal
import time
import sys

def handler_stop_signals(signum, frame):
    raise exitProgram

class exitProgram(KeyboardInterrupt):
    pass

signal.signal(signal.SIGTERM, handler_stop_signals)

try:
    while True:
        with open("/home/pi/killLog.txt", "a+") as log:
            log.write("Still alive!\n")
        time.sleep(1)
except KeyboardInterrupt:
    with open("/home/pi/killLog.txt", "a+") as log:
        log.write("Process killed successfully!\n")
    sys.exit(0)