import os
import subprocess
import time
from sensor import SHT20
import RPi.GPIO as GPIO
from datetime import datetime
from DF_Oxygen import *
    
# This is the humidy/temperature sensor.
sen0227 = SHT20(1, 0x40)

# This is the oxygen sensor.
sen0322 = (1, 0x73)

# Set input pins for capacitive moisture sensor and LED strip.
GPIO.setmode(GPIO.BCM)
sen0308 = 18
GPIO.setup(sen0308,GPIO.IN)
growLights = 26
GPIO.setup(growLights,GPIO.OUT)

# Set input pins for Step Motor 28BYJ-48.
stepXPins = [5,6,13,19]
stepYPins = [27,22,23,24]
for pin in stepXPins:
    GPIO.setup(pin,GPIO.OUT)
    GPIO.output(pin, False)
for pin in stepYPins:
    GPIO.setup(pin,GPIO.OUT)
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

# Function to actuate dual motor peristaltic pump.
def pumpWater():
    global seqCounter, stepCounter, revs
    while seqCounter < 511*revs:  # Number of sequences required for one revolution.
        for pin in range(0, 4):
            xpin = stepXPins[pin]
            ypin = stepYPins[-pin]
            if seq[stepCounter][pin]!=0:
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

# Function to check Little Gem root zone moisture.
def checkMoisture(sen0308):
    global seqCounter, stepCounter, revs
    if GPIO.input(sen0308):
        print("\nLittle Gem is thirsty, now watering!")
        pumpWater()
        seqCounter = 0

def calibrateOxygen():
    OXYGEN_CONECTRATION = 20.9  # The current concentration of oxygen in the air.
    OXYGEN_MV = 0  # The value marked on the sensor, Do not use must be assigned to 0.
    IIC_MODE = 0x01  # default use IIC1
    '''
      The first  parameter is to select iic0 or iic1
      The second parameter is the iic device address
      The default address for iic is ADDRESS_3
      ADDRESS_0                 = 0x70
      ADDRESS_1                 = 0x71
      ADDRESS_2                 = 0x72
      ADDRESS_3                 = 0x73 
    '''
    oxygen = DFRobot_Oxygen_IIC(IIC_MODE, ADDRESS_3)
    oxygen.calibrate(OXYGEN_CONECTRATION, OXYGEN_MV)
    print("oxygen calibrate success")
    time.sleep(1)


# Function to check Little Gem root zone oxygen.
def checkOxygen():
    # print("No oxygen, help!")
    IIC_MODE = 0x01  # default use IIC1
    COLLECT_NUMBER = 10
    oxygen = DFRobot_Oxygen_IIC(IIC_MODE, ADDRESS_3)
    oxygen_data = oxygen.get_oxygen_data(COLLECT_NUMBER)
    print("oxygen concentration is %4.2f %%vol" % oxygen_data)
    time.sleep(1)

# Function to capture image using Raspberry Pi Camera.
def captureImage(date):
    # Create directory for image storage.
    pwd = os.getcwd()
    if not os.path.exists(pwd + '/Images'):
        os.mkdir(pwd + '/Images')
    os.chdir(pwd + '/Images')
    print("\nSay cheese Little Gem!")
    subprocess.run(["libcamera-jpeg", "-o", date + ".jpeg"])  # Capture image.
    os.chdir('..')  # Return to EAT-pi directory.
        
# Return moisture level to terminal.
GPIO.add_event_detect(sen0308, GPIO.BOTH, bouncetime=300)
GPIO.add_event_callback(sen0308, checkMoisture)

# Create file for data logging.
file = open('eatLog.txt', 'w+')

# While true loop to run program, use CTRL + C to exit and cleanup pins.
try:
    while True:
        GPIO.output(growLights, GPIO.HIGH)
        #subprocess.run(["sudo", "service", "htpdate", "force-reload"])  # Force time synchronization.
        date = datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")
        data = sen0227.all()
        humid = data[0]
        temp = data[1]
        #captureImage(date)
        with open('eatLog.txt', "a") as log:
            checkMoisture(sen0308)
            checkOxygen()
            out = "\n" + date + "\n" + str(temp) + "\n" + str(humid) + "\n"
            log.write(out)
        print(out)
        time.sleep(5)
except KeyboardInterrupt:
    print("\n------------------\nEAT SYSTEM OFFLINE\n------------------")
    GPIO.cleanup()