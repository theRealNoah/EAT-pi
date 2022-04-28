#!/usr/bin/env python3

import os
import subprocess
import time
from sensor import SHT20
import RPi.GPIO as GPIO
from datetime import datetime
from DF_Oxygen import *
import matplotlib.pyplot as plt
from gpiozero import CPUTemperature
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import numpy
import signal
import sys

# Steps for software defined termination
# Establish ssh with Pi and use ps aux | grep eatMain.py
# This returns process numbers
# Use sudo kill [process number] for each process

# Allows for eatMain.py to be terminated when run from boot
# Raises exception when sudo kill signal is detected
def handler_stop_signals(signum, frame):
    raise exitProgramError

# Define exception as for exiting for both KeyboardInterrupt
class exitProgramError(KeyboardInterrupt):
    pass

# Setup listener
signal.signal(signal.SIGTERM, handler_stop_signals)

# Google Authentication for Uploading Plots and Images
gauth = GoogleAuth()
# Try to load saved client credentials
gauth.LoadCredentialsFile("google_creds.txt")
if gauth.credentials is None:
    # Authenticate if they're not there
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    # Refresh them if expired
    print('token expired')
    gauth.Refresh()
else:
    # Initialize the saved creds
    gauth.Authorize()
# Save the current credentials to a file
gauth.SaveCredentialsFile("google_creds.txt")
drive = GoogleDrive(gauth)
latestImageFolder = "1cmch7qs3WFkpS8GLzCbclByMP7uN3_dq"
archiveImageFolder = "1UBtqvBXPVuEiwwb6G7ogHJ5iie4RP3Nv"
plotFolder = "1PXfi9Ked4a14cCu0gaI6VATY_K6fNgld"

# Remove Current Images
path = "\'" + latestImageFolder + "\'" + " in parents and trashed=false"
fileList = drive.ListFile({'q': path}).GetList()
if fileList:
    for file in fileList:
        file.Trash()

path = "\'" + archiveImageFolder + "\'" + " in parents and trashed=false"
fileList = drive.ListFile({'q': path}).GetList()
if fileList:
    for file in fileList:
        file.Trash()

path = "\'" + plotFolder + "\'" + " in parents and trashed=false"
fileList = drive.ListFile({'q': path}).GetList()
if fileList:
    for file in fileList:
        file.Trash()

# Create file for data logging.
fileHeaders = ["Time", "Temp (F)", "Humidity", "Oxygen", "CPU Temp,"]
with open("eatLog.txt", "w+") as newFile:
    newFile.write(",".join(fileHeaders))
    # Begin a Timer
    startTime = time.perf_counter()

# Create file for error logging
with open("/home/pi/EAT-pi/errorLog.txt", "w+") as log:
    log.write("EAT ERROR LOG:\n")

# Set the naming convention for pins to use the numbers
# after GPIO{}
# e.g. GPIO18
GPIO.setmode(GPIO.BCM)

# This is the humidity/temperature sensor, SHT20(Channel, Address).
sen0227 = SHT20(1, 0x40)

# Set the GPIO Pin for powering lights 'SPI0 CEO0'
growLights = 8
GPIO.setup(growLights, GPIO.OUT)
isLightOn = False

# Set input pins for Step Motor 28BYJ-48, inputPins = [IN1, IN2, IN3, IN4].
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
seq = [
    [1, 0, 0, 1],
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1],
]

stepCount = len(seq)
stepDir = -2  # Set to 1 or 2 for clockwise, negative for counter-clockwise.
stepCounter = 0
seqCounter = 0
revs = 30  # Edit the revolutions needed to deliver water.

# Setup raw data arrays and sample arrays.
sampleStartTime = 0
sampleEndTime = 0
humidityRaw = []
temperatureRaw = []
oxygenRaw = []
cpuTempRaw = []
humiditySamples = []
temperatureSamples = []
oxygenSamples = []
cpuTempSamples = []
elapsedTimes = []
sampleCounter = 0
# Adjust this variable to increase raw data points per sample.
rawDataPerSample = 10


# Function to actuate dual motor peristaltic pump.
def pumpWater():
    global seqCounter, stepCounter, revs
    while seqCounter < 511 * revs:  # Number of sequences required for one revolution.
        # if seqCounter % 511 == 0:
            # print('Rev: ', seqCounter)
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
            stepCounter = stepCount + stepDir
            seqCounter += 1
        time.sleep(3 / float(1000))  # Pause before next sequence.
    seqCounter = 0


# Function to check Little Gem root zone moisture and temperature.
def getTemperatureAndHumidity():
    data = sen0227.all()
    # data[0],  is a tuple with ('Humidity', ['RH'])
    # data[1], is a tuple('Temperature', ['C', 'F', 'K'])
    return data[0], data[1]


# Function to check Little Gem root zone oxygen.
def getOxygen():
    # Code below from manufacturer.
    IIC_MODE = 0x01  # default use IIC1
    COLLECT_NUMBER = 10
    oxygen = DFRobot_Oxygen_IIC(IIC_MODE, ADDRESS_3)
    oxygen_data = oxygen.get_oxygen_data(COLLECT_NUMBER)
    return oxygen_data


# Function to return CPU temperature over time.
def getCPUTemp():
    data = CPUTemperature()
    # Convert Temperature from C to F
    return (data.temperature*1.8) + 32

# Function to Sample and Average Data and save to Global Variables
def sampleData():
    global sampleStartTime, humidityRaw, temperatureRaw, oxygenRaw, cpuTempRaw, sampleEndTime, elapsedTimes
    global humiditySamples, temperatureSamples, oxygenSamples, cpuTempSamples
    # Capture Raw Data Points
    sampleStartTime = time.perf_counter() - startTime  # Current Elapsed Time
    for i in range(rawDataPerSample):
        o2 = getOxygen()
        humidity, temp = getTemperatureAndHumidity()
        cpuTemp = getCPUTemp()
        # Add Raw to the Total List of Raw
        humidityRaw.append(humidity[0])  # Access First Element of Humidity Tuple to read value
        temperatureRaw.append(temp[1])  # Access Second Element of Temperature Tuple to read Fahrenheit
        oxygenRaw.append(o2)
        cpuTempRaw.append(cpuTemp)
    sampleEndTime = round(time.perf_counter() - startTime,2)
    elapsedTimes.append(sampleEndTime)

    # Append the average of the latest samples to new arrays
    humiditySamples.append(avg(humidityRaw[-rawDataPerSample:]))
    temperatureSamples.append(avg(temperatureRaw[-rawDataPerSample:]))
    oxygenSamples.append(avgRemoveOutlier(oxygenRaw[-rawDataPerSample:]))
    cpuTempSamples.append(avg(cpuTempRaw[-rawDataPerSample:]))


# Data analysis to determine if the plant needs watering.
def isPlantThirsty(humidity):
    # TODO: determine sampling of data and determine when the plant should actually need water
    threshold = 50  # update this
    if humidity < threshold:
        print("\nLittle Gem is thirsty, now watering!")
        return True
    else:
        print("\nLittle Gem is living its best life, Wait to Water!")
        return False


def actuateGrowLights(currentTime, forceOn=False, forceOff=False):
    global isLightOn
    # Actuate the Lights if time is between 0-8hrs and Turn off lights between hours 8-24
    # If current time divided by 86400 remainder is less than 28800, turn ON.
    # i.e. Current time of the current day.
    if forceOn:
        print('forced on')
        GPIO.output(growLights, GPIO.HIGH)
        isLightOn = True
    elif forceOff:
        print('forced off')
        GPIO.output(growLights, GPIO.LOW)
        isLightOn = False
    else:
        if currentTime % 86400 < 28800:
            # To turn on LED Power MOSFET Circuit.
            GPIO.output(growLights, GPIO.HIGH)
            isLightOn = True
            print('Time turn on lights')
        else:
            # To turn off LED Power MOSFET Circuit.
            GPIO.output(growLights, GPIO.LOW)
            isLightOn = False
            print('Time turn off lights')


def avg(data):
    return round(sum(data) / len(data),2)

def avgRemoveOutlier(data):
    elements = numpy.array(data)
    mean = numpy.mean(elements, axis=0)
    sd = numpy.std(elements, axis=0)

    finalList = [x for x in data if (x > mean - 2 * sd)]
    finalList = [x for x in finalList if (x < mean + 2 * sd)]
    weightedMean = mean
    if finalList:
        weightedMean = numpy.mean(finalList, axis=0)
    print('Normal Average ' + str(mean))
    print('Average Minus Outliers ' + str(weightedMean))
    return round(weightedMean, 2)

# Function to capture image using Raspberry Pi Camera.
def captureImage(timestamp):
    if not isLightOn:
        actuateGrowLights(timestamp, forceOn=True)
        time.sleep(3)
    pwd = os.getcwd()
    if not os.path.exists(pwd + "/Images"):  # Create directory for image storage.
        os.mkdir(pwd + "/Images")
    os.chdir(pwd + "/Images")
    print("\nSay cheese Little Gem!")
    subprocess.run(["libcamera-jpeg", "--rotation", "180", "-n", "-o", str(timestamp) + ".jpeg"])  # Capture image.
    os.chdir("..")  # Return to EAT-pi directory.
    if not isLightOn:
        actuateGrowLights(timestamp, forceOff=True)
        time.sleep(3)

def writeLog():
    with open("eatLog.txt", "a") as log:
        dataOut = [
            str(elapsedTimes[-1]),
            str(temperatureSamples[-1]),
            str(humiditySamples[-1]),
            str(oxygenSamples[-1]),
            str(cpuTempSamples[-1]),
        ]
        log.write(",".join(dataOut) + ",\n")
        print(dataOut)

def plotData():
    # Sensor Temperature vs. Elapsed Time
    fig, axs = plt.subplots(4, sharex=True,layout='tight', figsize=(8, 6))

    fig.suptitle('EAT Status', fontsize='large')
    color_cycle = plt.rcParams['axes.prop_cycle']()
    degree_sign = u'\N{DEGREE SIGN}'
    # plt.title("Sensor Temperature (F) vs. Elapsed Time")
    axs[0].plot(elapsedTimes, temperatureSamples, **next(color_cycle))
    axs[0].set_ylabel('F'+degree_sign)
    axs[0].set_title('Root Temperature', fontsize='x-small')
    axs[0].ticklabel_format(useOffset=False, style='plain')

    # CPU Temperature vs. Elapsed Time
    axs[1].plot(elapsedTimes, cpuTempSamples, **next(color_cycle))
    axs[1].set_ylabel('F'+degree_sign)
    axs[1].set_title('CPU Temperature', fontsize='x-small')
    axs[1].ticklabel_format(useOffset=False, style='plain')

    # Relative Humidity vs. Elapsed Time
    axs[2].plot(elapsedTimes, humiditySamples, **next(color_cycle))
    axs[2].set_ylabel('%')
    axs[2].set_title('Relative Humidity', fontsize='x-small')
    axs[2].ticklabel_format(useOffset=False, style='plain')

    # Oxygen vs. Elapsed Time
    axs[3].plot(elapsedTimes, oxygenSamples,  **next(color_cycle))
    axs[3].set_ylabel('%')
    axs[3].set_title('Oxygen Concentration', fontsize='x-small')
    axs[3].set_xlabel('Elapsed Time (s)', fontsize='x-small')
    axs[3].ticklabel_format(useOffset=False, style='plain')

    # handles, labels = axs[3].get_legend_handles_labels()
    # fig.legend(handles, labels, loc='upper center')
    # fig.legend(bbox_to_anchor=(1, 1),
    #           bbox_transform=fig.transFigure)
    # Hide x labels and tick labels for all but bottom plot.
    for ax in axs:
        ax.label_outer()

    pwd = os.getcwd()
    if not os.path.exists(pwd + "/Plots"):  # Create directory for image storage.
        os.mkdir(pwd + "/Plots")
    os.chdir(pwd + "/Plots")
    plt.savefig("EAT_Status.png")
    print('Plot Saved')
    plt.close()
    os.chdir("..")  # Return to EAT-pi directory.


def sortingImages(image):
    intValue = int(image.split('.')[0])
    return intValue

def uploadImages():
    # Populate uploadFileList with images in oldest to recent order with latest file being last.
    pwd = os.getcwd()
    os.chdir(pwd + "/Images")
    images = os.listdir()
    if "google_creds.txt" in images:
        images.remove("google_creds.txt")
    images.sort(key=sortingImages)
    uploadFileList = images
    print(uploadFileList)
    for upload in uploadFileList:
        str = "\'" + latestImageFolder + "\'" + " in parents and trashed=false"
        fileList = drive.ListFile({'q': str}).GetList()
        # Move Latest Photo to Archive
        if fileList:
            file = fileList[0]
            filename = file['title']
            file.GetContentFile(filename)
            gfile = drive.CreateFile({'parents': [{'id': archiveImageFolder}]})
            gfile.SetContentFile(filename)
            gfile.Upload()
            file.Trash()
        # Upload latest photo
        gfile = drive.CreateFile({'parents': [{'id': latestImageFolder}]})
        # Read file and set it as the content of this instance.
        gfile.SetContentFile(upload)
        gfile.Upload()
        print("Finished Upload of " + upload)
        os.remove(upload)
    print(os.listdir())
    os.chdir("..")  # Return to EAT-pi directory.

def uploadPlots():
    # Populate plotFiles with the plots that need to be uploaded
    pwd = os.getcwd()
    os.chdir(pwd + "/Plots")
    images = os.listdir()
    plotFiles = images
    if "google_creds.txt" in images:
        images.remove("google_creds.txt")
    for plot in plotFiles:
        str = "\'" + plotFolder + "\'" + " in parents and trashed=false"
        fileList = drive.ListFile({'q': str}).GetList()
        # Move Latest Photo to Archive
        if fileList:
            file = fileList[0]
            file.Trash()
        # Upload the Plot
        gfile = drive.CreateFile({'parents': [{'id': plotFolder}]})
        # Read file and set it as the content of this instance.
        gfile.SetContentFile(plot)
        gfile.Upload()
        print("Finished Plot Upload")
        os.remove(plot)
    os.chdir("..")  # Return to EAT-pi directory.

def uploadData():
    print('Begin Upload Images')
    uploadImages()
    print('Begin Upload Plots')
    uploadPlots()

# While true loop to run program, use CTRL + C to exit and cleanup pins.
try:
    while True:
        # Read raw values from sensors and save average to global data arrays
        sampleData()

        # Pass the current time to LED control function.
        actuateGrowLights(sampleEndTime)

        # Pass the latest sample to the decision making function.
        if isPlantThirsty(humiditySamples[-1]):
            pumpWater()

        # Take image of the pi
        captureImage(int(sampleEndTime))

        # Outputs Text File for Logging Data
        writeLog()

        # Generates Plot based on all samples continuously
        plotData()

        sampleCounter += 1
        # Upload Data every a certain amount of samples
        if sampleCounter % 5 == 0:
            uploadData()
        # Sleep between Sample Times
        time.sleep(5)
except KeyboardInterrupt as e:
    print("\n------------------\nEAT SYSTEM OFFLINE\n------------------")
    with open("/home/pi/EAT-pi/errorLog.txt", "a+") as log:
        log.write(str(e))
        log.write("\nEAT has encountered at time = " + str(sampleEndTime) + "\n")
    GPIO.cleanup()
    sys.exit(0)
