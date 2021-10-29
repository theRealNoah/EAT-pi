from sensor import SHT20
from time import sleep
import smbus2
import RPi.GPIO as GPIO

# This is the humidy/temperature sensor.
sht = SHT20(1, 0x40)

# Set input pins for root zone moisture sensor.
GPIO.setmode(GPIO.BOARD)
sen0308 = 23
GPIO.setup(sen0308,GPIO.IN)

# To-Do add in another condition for while loop...
while True:
    
    data = sht.all()
    humid = data[0]
    temp = data[1]
    
    moist = GPIO.input(sen0308)
    
    
    print(str(temp) + str(humid) + " Moisture:" + str(moist))
    sleep(5)