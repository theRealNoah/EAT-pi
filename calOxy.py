from DF_Oxygen import *
import RPi.GPIO as GPIO
import sys

GPIO.setmode(GPIO.BCM)

# Create file for error logging
with open("o2Cal.txt", "a") as log:
    log.write("EAT Oxygen Sensor Calibration LOG:\n")

# Function to check Little Gem root zone oxygen.
def getOxygen():
    # Code below from manufacturer.
    IIC_MODE = 0x01  # default use IIC1
    COLLECT_NUMBER = 10
    oxygen = DFRobot_Oxygen_IIC(IIC_MODE, ADDRESS_3)
    oxygen_data = oxygen.get_oxygen_data(COLLECT_NUMBER)
    return oxygen_data

counter = 0
oxygenRaw = []

try:
    while(counter < 180):
        o2 = getOxygen()
        oxygenRaw.append(o2)
        print("oxygen concentration is %4.2f %%vol" % o2)
        counter += 1
        time.sleep(1)
        with open("o2Cal.txt", "a") as log:
            log.write(oxygenRaw)

except KeyboardInterrupt as e:
    print("\n------------------\nEAT SYSTEM OFFLINE\n------------------")
    GPIO.cleanup()
    sys.exit(0)
