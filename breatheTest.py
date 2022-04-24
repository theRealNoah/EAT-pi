from DF_Oxygen import *
import RPi.GPIO as GPIO
import sys
from sensor import SHT20
import csv

GPIO.setmode(GPIO.BCM)

# Create file for before cal
with open("breatheTest.txt", "w") as log:
    log.write("BREATHE TEST SHOWING TEMPERATURE/HUMIDITY/OXYGEN SENSOR:\n")

# Function to check Little Gem root zone oxygen.
def getOxygen():
    # Code below from manufacturer.
    IIC_MODE = 0x01  # default use IIC1
    COLLECT_NUMBER = 10
    oxygen = DFRobot_Oxygen_IIC(IIC_MODE, ADDRESS_3)
    oxygen_data = oxygen.get_oxygen_data(COLLECT_NUMBER)
    return oxygen_data

# This is the humidity/temperature sensor, SHT20(Channel, Address).
sen0227 = SHT20(1, 0x40)

# Function to check Little Gem root zone moisture and temperature.
def getTemperatureAndHumidity():
    data = sen0227.all()
    # data[0],  is a tuple with ('Humidity', ['RH'])
    # data[1], is a tuple('Temperature', ['C', 'F', 'K'])
    return data[0], data[1]

counter = 0
oxygenRaw = []
humidityRaw = []
tempRaw = []

try:
    while True:
        o2 = getOxygen()
        humidity, temp = getTemperatureAndHumidity()
        h = humidity[0]
        temp_f = temp[1]
        # oxygenRaw.append(str(o2))
        # humidityRaw.append((str(h)))
        # tempRaw.append((str(temp_f)))
        # print("oxygen concentration is %4.2f %%vol" % o2)
        out = str(counter) + "," + str(o2) + "," + str(h) + "," + str(temp_f) + "\n"
        print(out)
        with open("breatheTest.txt", "a") as log:
            log.write(str(counter) + "," + str(o2) + "," + str(h) + "," + str(temp_f) + "\n")
        counter += 1
        time.sleep(1)

    print('Finished Breathe Test')
except KeyboardInterrupt as e:
    print("\n------------------\nEAT SYSTEM OFFLINE\n------------------")
    sys.exit(0)
