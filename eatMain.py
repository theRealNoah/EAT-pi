import subprocess
import time
from sensor import SHT20
import RPi.GPIO as GPIO
from datetime import datetime
    
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

# Create file for data logging.
file = open('eatLog.txt','w+')

# Define advanced sequence as shown in manufacturers datasheet.
seq = [[1,0,0,1],
       [1,0,0,0],
       [1,1,0,0],
       [0,1,0,0],
       [0,1,1,0],
       [0,0,1,0],
       [0,0,1,1],
       [0,0,0,1]]
 
stepCount = len(seq)
stepDir = 2 # Set to 1 or 2 for clockwise
            # Set to -1 or -2 for counter-clockwise
 
# Initialise variables
stepCounter = 0
seqCounter = 0
revs = 1 # Edit the revolutions needed to deliver water.
waitTime = 3/float(1000)

# Create a function to actuate motor.
def pumpwater():
    global seqCounter, stepCounter, revs
    while seqCounter < 511*revs: # Number of sequences required for one revolution.
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
        if (stepCounter >= stepCount):
            stepCounter = 0
            seqCounter += 1
        if (stepCounter < 0):
            stepCounter = stepCount+stepDir
            seqCounter += 1
 
    # Wait before moving on.
        time.sleep(waitTime)

# Create a function to check plant moisture.
def checkmoisture(sen0308):
    global seqCounter, stepCounter, revs
    if GPIO.input(sen0308):
        print("\nPlant is thirsty, now watering!")
        pumpwater()
        seqCounter = 0

def captureImage(date):
    subprocess.run(["libcamera-jpeg", "-o", date + ".jpeg"])
        
# Return moisture level to terminal.
GPIO.add_event_detect(sen0308, GPIO.BOTH, bouncetime=300)
GPIO.add_event_callback(sen0308, checkmoisture)

# While true loop to run program, use CTRL + C to exit and cleanup pins.
try:
    while True:
        GPIO.output(growLights,GPIO.HIGH)
        date = datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")
        data = sen0227.all()
        humid = data[0]
        temp = data[1]
        captureImage(date)
        with open('eatLog.txt', "a") as log:
            checkmoisture(sen0308)
            out = "\n" + date + "\n" + str(temp) + "\n" + str(humid) + "\n"
            log.write(out)
        print(out)
        time.sleep(5)
except KeyboardInterrupt:
    print("\n------------------\nEAT SYSTEM OFFLINE\n------------------")
    GPIO.cleanup()