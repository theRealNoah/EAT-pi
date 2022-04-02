import os
import subprocess
import time
from sensor import SHT20
import RPi.GPIO as GPIO
from datetime import datetime
from DF_Oxygen import *

# Create file for data logging.
fileHeaders = ["Time", "Temp (F)", "Humidity", "Oxygen"]
with open('eatLog.txt', 'w+') as newFile:
    newFile.write(",".join(fileHeaders))
    # Begin a Timer
    startTime = time.perf_counter()

# Todo: Check if txt exists, if so read latest elapsed time, if not, create new timer


# Set the naming convention for pins to use the numbers after GPIO{}
# e.g. GPIO18
GPIO.setmode(GPIO.BCM)

# This is the humidity/temperature sensor.
# SHT20 takes i2c channel and address as parameters
sen0227 = SHT20(1, 0x40)

# Set the GPIO Pin for powering lights
# TODO: This needs to be updated to support MOSFET / Thyristor Circuit
growLights = 26
GPIO.setup(growLights, GPIO.OUT)

# Set input pins for Step Motor 28BYJ-48.
# Format inputPins = [IN1, IN2, IN3, IN4]
# Motor X
stepXPins = [4, 17, 18, 27]
# Motor Y
stepYPins = [22, 23, 24, 25]

for pin in stepXPins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, False)
for pin in stepYPins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, False)

# Define sequence as shown in manufacturers data sheet.
seq = [[1,0,0,1],
       [1,0,0,0],
       [1,1,0,0],
       [0,1,0,0],
       [0,1,1,0],
       [0,0,1,0],
       [0,0,1,1],
       [0,0,0,1]]
 
stepCount = len(seq)
stepDir = 2  # Set to 1 or 2 for clockwise, negative for counter-clockwise.
stepCounter = 0
seqCounter = 0
revs = 1  # Edit the revolutions needed to deliver water.


# Initialize arrays for saving raw data
humidityRaw = []
temperatureRaw = []
oxygenRaw = []
# Sample Data
humiditySamples = []
temperatureSamples = []
oxygenSamples = []
elapsedTimes = []

rawDataPerSample = 10


# Function to actuate dual motor peristaltic pump.
def pumpWater():
    global seqCounter, stepCounter, revs
    while seqCounter < 511*revs:  # Number of sequences required for one revolution.
        for pin in range(0, 4):
            xpin = stepXPins[pin]
            ypin = stepYPins[-pin]
            if seq[stepCounter][pin] != 0:
                GPIO.output(xpin, True)
                GPIO.output(ypin, True)
            else:
                GPIO.output(xpin, False)
                GPIO.output(ypin, False)
        stepCounter += stepDir
 
    # When we reach the end of the sequence, start again.
        if stepCounter >= stepCount:
            stepCounter = 0
            seqCounter += 1
        if stepCounter < 0:
            stepCounter = stepCount+stepDir
            seqCounter += 1
        time.sleep(3/float(1000))  # Pause before next sequence.
    seqCounter = 0


# Function to check Little Gem root zone moisture and temperature
def getTemperatureAndHumidity():
    data = sen0227.all()
    # Todo: Check temperature returns and choose either C,F,K
    return data[0], data[1]


# Function to check Little Gem root zone oxygen.
def getOxygen():
    # Code below from manufacturer.
    IIC_MODE = 0x01  # default use IIC1
    COLLECT_NUMBER = 10
    oxygen = DFRobot_Oxygen_IIC(IIC_MODE, ADDRESS_3)
    oxygen_data = oxygen.get_oxygen_data(COLLECT_NUMBER)
    return oxygen_data


# Use sampling/data analysis to determine if the plant needs water
def isPlantThirsty(humidity):
    # todo: determine sampling of data and determine when the plant should actually need water
    threshold = 100 # update this
    if humidity < threshold:
        print("\nLittle Gem is thirsty, now watering!")
        return True
    else:
        print("\nLittle Gem is living its best life, Wait to Water!")
        return False


def avg(data):
    return sum(data)/len(data)


# Function to capture image using Raspberry Pi Camera.
def captureImage(date):
    pwd = os.getcwd()
    if not os.path.exists(pwd + '/Images'):  # Create directory for image storage.
        os.mkdir(pwd + '/Images')
    os.chdir(pwd + '/Images')
    print("\nSay cheese Little Gem!")
    subprocess.run(["libcamera-jpeg", "-o", date + ".jpeg"])  # Capture image.
    os.chdir('..')  # Return to EAT-pi directory.


# While true loop to run program, use CTRL + C to exit and cleanup pins.
try:
    while True:
        # Todo: Sensor Calibration
        # Taking lots of data to normalize to a threshold

        # Capture Raw Data Points
        sampleStartTime = time.perf_counter() - startTime  # Current Elapsed Time
        for i in range(rawDataPerSample):
            o2 = getOxygen()
            humidity, temp = getTemperatureAndHumidity()
            # Add Raw to the Total List of Raw
            humidityRaw.append(humidity)
            temperatureRaw.append(temp)
            oxygenRaw.append(o2)
        sampleEndTime = time.perf_counter() - startTime
        elapsedTimes.append(sampleEndTime)

        # Append the average of the latest samples to new arrays
        humiditySamples.append(avg(humidityRaw[-rawDataPerSample:]))
        temperatureSamples.append(avg(temperatureRaw[-rawDataPerSample:]))
        oxygenSamples.append(avg(oxygenRaw[-rawDataPerSample:]))

        # Pass the sample to the decision making function
        if isPlantThirsty(humiditySamples[-1]):
            pumpWater()

        # Todo: Put the grow lights on a timer by using elapsed time, so whatever interval we determine
        GPIO.output(growLights, GPIO.HIGH)

        #subprocess.run(["sudo", "service", "htpdate", "force-reload"])  # Force time synchronization.
        date = datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")
        # captureImage(date)

        with open('eatLog.txt', "a") as log:
            dataOut = [str(elapsedTimes[-1]),
                       str(temperatureSamples[-1]),
                       str(humiditySamples[-1]),
                       str(oxygenSamples[-1])]
            log.write(".")
            print(dataOut)

        # Todo: Data Uplink -- CLOUD NOW -- make an account
        # Todo: Data Plotting
        # Todo: Live GUI


        # Sleep between Sample Times
        time.sleep(5)
except KeyboardInterrupt:
    print("\n------------------\nEAT SYSTEM OFFLINE\n------------------")
    GPIO.cleanup()