from DF_Oxygen import *
import RPi.GPIO as GPIO
import sys

GPIO.setmode(GPIO.BCM)

# Create file for before cal
with open("o2BeforeCal.txt", "w") as log:
    log.write("EAT Oxygen Sensor Calibration BEFORE LOG:\n")


# Create file for after cal
with open("o2AfterCal.txt", "w") as log:
    log.write("EAT Oxygen Sensor Calibration AFTER LOG:\n")


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
        oxygenRaw.append(str(o2))
        print("oxygen concentration is %4.2f %%vol" % o2)
        counter += 1
        time.sleep(1)
        with open("o2BeforeCal.txt", "a") as log:
            log.write(",".join(oxygenRaw))
    print('Three Minutes Have Passed')
    time.sleep(10)
    counter = 0
    oxygenRaw = []
    while(counter < 180):
        if counter == 150:
            print('Two Minutes Up')
        o2 = getOxygen()
        oxygenRaw.append(str(o2))
        print("oxygen concentration is %4.2f %%vol" % o2)
        counter += 1
        time.sleep(1)
        with open("o2AfterCal.txt", "a") as log:
            log.write(",".join(oxygenRaw))
    print('Finished Cal')
except KeyboardInterrupt as e:
    print("\n------------------\nEAT SYSTEM OFFLINE\n------------------")
    sys.exit(0)
