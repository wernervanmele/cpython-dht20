# DHT20 I2C Humidity and Temperature sensor
Circuit Python version of my esp-idf version https://github.com/wernervanmele/esp-idf-dht20  
usage:  
copy dht20.py to your local folder and add to your program:  

```python
from dht20 import DHT20
import busio

i2c = busio.I2C(SCL, SDA, frequency=400000)
my_sensor = DHT20(i2c)
```