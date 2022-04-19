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
latest_plant_image_folder_id = "1cmch7qs3WFkpS8GLzCbclByMP7uN3_dq"
archive_plant_image_folder_id = "1UBtqvBXPVuEiwwb6G7ogHJ5iie4RP3Nv"
plot_folder_id = "1PXfi9Ked4a14cCu0gaI6VATY_K6fNgld"


# Create file for data logging.
fileHeaders = ["Time", "Temp (F)", "Humidity", "Oxygen", "CPU Temp"]
with open("eatLog.txt", "w+") as newFile:
    newFile.write(",".join(fileHeaders))
    # Begin a Timer
    startTime = time.perf_counter()

# TODO: Check if txt exists, if so read latest elapsed time, if not, create new timer


# Set the naming convention for pins to use the numbers
# after GPIO{}
# e.g. GPIO18
GPIO.setmode(GPIO.BCM)

# This is the humidity/temperature sensor, SHT20(Channel, Address).
sen0227 = SHT20(1, 0x40)

# Set the GPIO Pin for powering lights
# TODO: This needs to be updated to support MOSFET / Thyristor Circuit
growLights = 26
GPIO.setup(growLights, GPIO.OUT)

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
stepDir = 2  # Set to 1 or 2 for clockwise, negative for counter-clockwise.
stepCounter = 0
seqCounter = 0
revs = 1  # Edit the revolutions needed to deliver water.

# Setup raw data arrays and sample arrays.
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
    # TODO: Pip install gpiozero!
    data = CPUTemperature()
    # Convert Temperature from C to F
    return (data.temperature*1.8) + 32


# Data analysis to determine if the plant needs watering.
def isPlantThirsty(humidity):
    # TODO: determine sampling of data and determine when the plant should actually need water
    threshold = 100  # update this
    if humidity < threshold:
        print("\nLittle Gem is thirsty, now watering!")
        return True
    else:
        print("\nLittle Gem is living its best life, Wait to Water!")
        return False


def avg(data):
    return sum(data) / len(data)


# Function to capture image using Raspberry Pi Camera.
def captureImage(timestamp):
    pwd = os.getcwd()
    if not os.path.exists(pwd + "/Images"):  # Create directory for image storage.
        os.mkdir(pwd + "/Images")
    os.chdir(pwd + "/Images")
    print("\nSay cheese Little Gem!")
    subprocess.run(["libcamera-jpeg", "-n", "-o", str(timestamp) + ".jpeg"])  # Capture image.
    os.chdir("..")  # Return to EAT-pi directory.

def sortingImages(image):
    intValue = int(image.split('.')[0])
    return intValue

def uploadImages():
    # Populate upload_file_list with images in oldest to recent order with latest file being last.
    pwd = os.getcwd()
    os.chdir(pwd + "/Images")
    images = os.listdir()
    if "google_creds.txt" in images:
        images.remove("google_creds.txt")
    images.sort(key=sortingImages)

    upload_file_list = images
    print('Right before images')
    print(images)
    for upload_file in upload_file_list:
        str = "\'" + latest_plant_image_folder_id + "\'" + " in parents and trashed=false"
        file_list = drive.ListFile({'q': str}).GetList()
        # Move Latest Photo to Archive
        if file_list:
            file = file_list[0]
            filename = file['title']
            file.GetContentFile(filename)
            gfile = drive.CreateFile({'parents': [{'id': archive_plant_image_folder_id}]})
            gfile.SetContentFile(filename)
            gfile.Upload()
            file.Trash()
        # Upload latest photo
        gfile = drive.CreateFile({'parents': [{'id': latest_plant_image_folder_id}]})
        # Read file and set it as the content of this instance.
        gfile.SetContentFile(upload_file)
        gfile.Upload()
        print('Finished Image Upload')
    os.chdir("..")  # Return to EAT-pi directory.

def uploadPlots():
    # Populate plot_files with the plots that need to be uploaded
    pwd = os.getcwd()
    os.chdir(pwd + "/Plots")
    images = os.listdir()
    plot_files = images
    print('Right before images')
    print(plot_files)
    for plot_file in plot_files:
        # Upload the Plot
        gfile = drive.CreateFile({'parents': [{'id': plot_folder_id}]})
        # Read file and set it as the content of this instance.
        gfile.SetContentFile(plot_file)
        gfile.Upload()
        print('Finished Plot File Upload')
    os.chdir("..")  # Return to EAT-pi directory.

# While true loop to run program, use CTRL + C to exit and cleanup pins.
try:
    while True:
        # TODO: Sensor Calibration
        # Taking lots of data to normalize to a threshold

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
        sampleEndTime = time.perf_counter() - startTime
        elapsedTimes.append(sampleEndTime)

        # Append the average of the latest samples to new arrays
        humiditySamples.append(avg(humidityRaw[-rawDataPerSample:]))
        temperatureSamples.append(avg(temperatureRaw[-rawDataPerSample:]))
        oxygenSamples.append(avg(oxygenRaw[-rawDataPerSample:]))
        cpuTempSamples.append(avg(cpuTempRaw[-rawDataPerSample:]))

        # Pass the sample to the decision making function
        if isPlantThirsty(humiditySamples[-1]):
            pumpWater()

        # TODO: Put the grow lights on a timer by using elapsed time, so whatever interval we determine
        # GPIO.output(growLights, GPIO.HIGH)

        # subprocess.run(["sudo", "service", "htpdate", "force-reload"])  # Force time synchronization.
        date = datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")
        captureImage(int(sampleEndTime))

        with open("eatLog.txt", "a") as log:
            dataOut = [
                str(elapsedTimes[-1]),
                str(temperatureSamples[-1]),
                str(humiditySamples[-1]),
                str(oxygenSamples[-1]),
                str(cpuTempSamples[-1]),
            ]
            log.write(",".join(dataOut))
            print(dataOut)

        # TODO: Data Uplink -- CLOUD NOW -- make an account

        # TODO: Data Plotting (Make this into one function and pass in data arrays)


        # Sensor Temperature vs. Elapsed Time
        fig, axs = plt.subplots(4, sharex=True)
        # plt.title("Sensor Temperature (F) vs. Elapsed Time")
        axs[0].plot(elapsedTimes, temperatureSamples)

        # CPU Temperature vs. Elapsed Time
        # plt.title("CPU Temperature (F) vs. Elapsed Time")

        axs[1].plot(elapsedTimes, cpuTempSamples)

        # Relative Humidity vs. Elapsed Time
        # plt.title("Relative Humidity vs. Elapsed Time")

        axs[2].plot(elapsedTimes, humiditySamples)

        # Oxygen vs. Elapsed Time
        # plt.title("Oxygen Level vs. Elapsed Time")

        axs[3].plot(elapsedTimes, oxygenSamples)

        # Hide x labels and tick labels for all but bottom plot.
        for ax in axs:
            ax.label_outer()
        # plt.show()

        pwd = os.getcwd()
        if not os.path.exists(pwd + "/Plots"):  # Create directory for image storage.
            os.mkdir(pwd + "/Plots")
        os.chdir(pwd + "/Plots")
        plt.savefig("EAT_Status.png")
        print('Plot Saved')
        os.chdir("..")  # Return to EAT-pi directory.

        plt.close()
        # TODO: Live GUI

        sampleCounter += 1
        if sampleCounter % 5 == 0:
            print('Begin Upload Images')
            uploadImages()
            print('Begin Upload Plots')
            uploadPlots()
        # Sleep between Sample Times
        time.sleep(5)
except KeyboardInterrupt:
    print("\n------------------\nEAT SYSTEM OFFLINE\n------------------")
    GPIO.cleanup()

