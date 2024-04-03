import busio
from board import *
import time
from dht20 import DHT20
       
i2c = busio.I2C(SCL, SDA, frequency=400000)
my_sensor = DHT20(i2c)
print(f"status: {my_sensor.__status()}") 

while not my_sensor.__is_calibrated():
    print(f"not calibrated apparently")
    time.sleep(1.0)

while True:        
    humidity, temperature = my_sensor.read_data()
    print(f"Humidity: {round(humidity,2)}%")
    print(f"Temperature: {round(temperature, 2)}C")
    time.sleep(2)
