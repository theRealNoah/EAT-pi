from sensor import SHT20
from time import sleep
import smbus2
import RPi.GPIO as GPIO

# This is the humidy/temperature sensor.

sht = SHT20(1, 0x40)

# Set input pins for root zone moisture sensor and LED.

GPIO.setmode(GPIO.BCM)
sen0308 = 17
GPIO.setup(sen0308,GPIO.IN)
LED = 27
GPIO.setup(LED,GPIO.OUT)

# Create a function to drive LED.

def callback(sen0308):
    if GPIO.input(sen0308):
        GPIO.output(27,GPIO.HIGH)
        return "\nPlant is thirsty!"
        
    else:
        GPIO.output(27,GPIO.LOW)
        return "\nPlant is hydrated!"

# Return moisture level to terminal and LED.

GPIO.add_event_detect(sen0308, GPIO.BOTH, bouncetime=300)
GPIO.add_event_callback(sen0308, callback)

# To-Do add in another condition for while loop...
while True:
    
    data = sht.all()
    humid = data[0]
    temp = data[1]
    
    print(str(temp) + str(humid) + str(callback(sen0308)))
    
    sleep(5)