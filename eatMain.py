import sys
import time
from sensor import SHT20
import RPi.GPIO as GPIO
from datetime import datetime
    
# This is the humidy/temperature sensor.
sht = SHT20(1, 0x40)

# Set input pins for root zone moisture sensor and LED.
GPIO.setmode(GPIO.BCM)
sen0308 = 17
GPIO.setup(sen0308,GPIO.IN)
growLights = 27
GPIO.setup(growLights,GPIO.OUT)

# Set input pins for Step Motor 28BYJ-48.
StepXPins = [23,24,5,6]
StepYPins = [22,25,16,13]
for pin in StepXPins:
    GPIO.setup(pin,GPIO.OUT)
    GPIO.output(pin, False)
for pin in StepYPins:
    GPIO.setup(pin,GPIO.OUT)
    GPIO.output(pin, False)

# Create file for data logging.
file = open('eatLog.txt','w+') 
date = datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")

# Define advanced sequence as shown in manufacturers datasheet.
Seq = [[1,0,0,1],
       [1,0,0,0],
       [1,1,0,0],
       [0,1,0,0],
       [0,1,1,0],
       [0,0,1,0],
       [0,0,1,1],
       [0,0,0,1]]
 
StepCount = len(Seq)
StepDir = 2 # Set to 1 or 2 for clockwise
            # Set to -1 or -2 for counter-clockwise
 
# Initialise variables
StepCounter = 0
SeqCounter = 0
Revs = 16 # Edit the revolutions needed to deliver water.
WaitTime = 3/float(1000)

# Create a function to actuate motor.
def pumpwater():
    global SeqCounter, StepCounter, Revs
    while SeqCounter < 511*Revs: # Number of sequences required for one revolution.
        for pin in range(0, 4):
            xpin = StepXPins[pin]
            ypin = StepYPins[-pin]
            if Seq[StepCounter][pin]!=0:
                GPIO.output(xpin, True)
                GPIO.output(ypin, True)
            else:
                GPIO.output(xpin, False)
                GPIO.output(ypin, False)
        StepCounter += StepDir
 
    # If we reach the end of the sequence, start again.
        if (StepCounter >= StepCount):
            StepCounter = 0
            SeqCounter += 1
        if (StepCounter < 0):
            StepCounter = StepCount+StepDir
            SeqCounter += 1
 
    # Wait before moving on
        time.sleep(WaitTime)

# Create a function to check plant moisture.
def checkmoisture(sen0308):
    global SeqCounter, StepCounter, Revs
    if GPIO.input(sen0308):
        print("\nPlant is thirsty, now watering!")
        pumpwater()
        SeqCounter = 0
        
# Return moisture level to terminal.
GPIO.add_event_detect(sen0308, GPIO.BOTH, bouncetime=300)
GPIO.add_event_callback(sen0308, checkmoisture)

# While true loop to run program, use CTRL + C to exit and cleanup pins.
try:

    while True:
        GPIO.output(growLights,GPIO.HIGH)
        with open('eatLog.txt', "a") as log:
            data = sht.all()
            humid = data[0]
            temp = data[1]
            checkmoisture(sen0308)
            out = "\n" + date + "\n" + str(temp) + "\n" + str(humid) + "\n"
            log.write(out)
        print(out)
        time.sleep(5)
except KeyboardInterrupt:
    print("\n------------------\nEAT SYSTEM OFFLINE\n------------------")
    GPIO.cleanup()
