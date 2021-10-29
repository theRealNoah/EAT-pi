from sensor import SHT20
from time import sleep
import smbus2

# This is the humidy/temperature sensor.
sht = SHT20(1, 0x40)

while True:
    
    data = sht.all()
    humid = data[0]
    temp = data[1]
    
    print("The temperature is " + str(temp) + " the humidity is " + str(humid) + " %")
    sleep(5)