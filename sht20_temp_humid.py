from sensor import SHT20
from time import sleep
import RPi.GPIO as GPIO
from datetime import datetime
    
# This is the humidy/temperature sensor.

sht = SHT20(1, 0x40)

# Set input pins for root zone moisture sensor and LED.

GPIO.setmode(GPIO.BCM)
sen0308 = 17
GPIO.setup(sen0308,GPIO.IN)
# LED = 27
# GPIO.setup(LED,GPIO.OUT)

# Create a function to drive LED.

def callback(sen0308):
    if GPIO.input(sen0308):
        #GPIO.output(27,GPIO.HIGH)
        return "\nPlant is thirsty!"
        
    else:
        #GPIO.output(27,GPIO.LOW)
        return "\nPlant is hydrated!"

# Return moisture level to terminal and LED.

GPIO.add_event_detect(sen0308, GPIO.BOTH, bouncetime=300)
GPIO.add_event_callback(sen0308, callback)

# Create file for data logging.

file = open('eatLog.txt','w+') 
date = datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")

# While true loop to run program, use CTRL + C to exit and cleanup pins.
try:

    while True:
        with open('eatLog.txt', "a") as log:
            data = sht.all()
            humid = data[0]
            temp = data[1]
            out = "\n" + date + "\n" + str(temp) + "\n" + str(humid) + str(callback(sen0308)) + "\n"
            log.write(out)
        print(out)
        sleep(5)
except KeyboardInterrupt:
    print("------------------\nEAT SYSTEM OFFLINE\n------------------")
    GPIO.cleanup()