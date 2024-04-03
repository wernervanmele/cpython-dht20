"""
sources:
https://www.geeksforgeeks.org/how-to-convert-bytes-to-int-in-python/
https://docs.python.org/3.11/library/struct.html
https://github.com/adafruit/Adafruit_CircuitPython_SGP40/blob/2426bfd646bac4f6fc0adca4f205df6387e8a130/adafruit_sgp40/__init__.py#L164
https://github.com/adafruit/Adafruit_CircuitPython_ADS1x15/blob/f8067390d689facde8db88c9e4acf37992e0a78f/adafruit_ads1x15/ads1x15.py
https://sparkbyexamples.com/python/python-sleep-milliseconds/
https://www.w3schools.com/python/python_try_except.asp#:~:text=The%20try%20block%20lets%20you,the%20try%2D%20and%20except%20blocks.
https://learn.adafruit.com/circuitpython-essentials?view=all
"""

import time
import os
from adafruit_bus_device.i2c_device import I2CDevice
from busio import I2C
from board import *

try:
    from typing import Dict, List, Optional
    from circuitpython_typing import ReadableBuffer
except ImportError:
    pass


class DHT20:
    """
    Class for the DHT20 I2C temperature and humidity sensor
    """
    def __init__(
        self,
        i2c: I2C,
        i2c_address: int = 0x38
        ):
        
        self.buf = bytearray(3)
        self.writebuff = bytearray(3)
        self.txbuffer = bytearray(3)
        self.i2c_device = I2CDevice(i2c, i2c_address)
        self.__reset_sensor()
              
    def __status(self) -> int:
        """
        Check status register, correct value should be 0x18
        """
        self.result = bytearray(1)
        with self.i2c_device as i2c:
            i2c.write_then_readinto(bytes([0x71]), self.result, in_end=1)
                
        return int.from_bytes(self.result, "big")
    
    def __is_calibrated(self) -> bool:
        """
        Check the is_calibrated bit
        """
        status_byte = self.__status()
        print(status_byte & 0x68)
        return bool((status_byte & 0x68) == 0x08)
    
    def __reset_registers(self, reg: int) -> bool:
        """
        reset register function, required by the reset sensor function
        """
        self.values = bytearray(3)
        self.txbuffer[0] = reg
        self.txbuffer[1] = 0x00
        self.txbuffer[2] = 0x00
        
        with self.i2c_device as i2c:
            i2c.write(self.txbuffer)
            time.sleep(5/1000)
            i2c.readinto(self.values, end=3)
            
        time.sleep(5/1000)
        self.writebuff[0] = (0xB0 | reg)
        self.writebuff[1] = self.values[1]
        self.writebuff[2] = self.values[2]

        try:
            with self.i2c_device as i2c:
                i2c.write(self.writebuff)
                time.sleep(5/1000)
        except:
            return False
        
        return True
     
    def __reset_sensor(self) -> None:
        """
        Reset certain registers in sensor to reset the complete sensor
        Is required to get the sensor working.
        """
        self.sensor_status = self.__status()
        self.counter = 0
        
        while (self.sensor_status != 0x18):
            self.__reset_registers(0x1B)
            self.__reset_registers(0x1C)
            self.__reset_registers(0x1E)
            self.sensor_status = self.__status()
            self.counter += 1
            print(f"Sensor status after reset: {self.sensor_status}")
            print(f"reset loop: {self.counter}")

        
    def __crc8(self, buffer: bytearray, num: int) -> int:
        """
        Calculate crc from data and match with value 6 in data buffer
        """
        crc = 0xFF
        for i in range(num):
            crc ^= (buffer[i])
            for q in range(8):
                if crc & 0x80:
                    crc = (
                        crc << 1
                        ) ^ 0x31
                else:
                    crc = crc << 1
        return crc & 0xFF


    def read_data(self) -> List[float]:
        """
        Read measured data from registers
        """
        self.txbuf = bytearray(3)
        self.txbuf[0] = 0xAC
        self.txbuf[1] = 0x33
        self.txbuf[2] = 0x00
        self.status_byte = bytearray(1)
        self.rxdata = bytearray(7)
        
        with self.i2c_device as i2c:
            i2c.write(self.txbuf)
            time.sleep(80/1000)
            
        with self.i2c_device as i2c:
            i2c.readinto(self.status_byte, end=1)
            
        while ((self.status_byte[0] >> 7) != 0):
            os.sched_yield()
            time.sleep(10/1000)
 
        with self.i2c_device as i2c:
            i2c.readinto(self.rxdata, end=7)
            
        get_crc = self.__crc8(self.rxdata, 6)

        if (self.rxdata[6] == get_crc):
            raw_hum = self.rxdata[1]
            raw_hum <<= 8
            raw_hum += self.rxdata[2]
            raw_hum <<= 4
            raw_hum += self.rxdata[3] >> 4
            float_humid = float((raw_hum / 1048576.0) * 100.0)
            
            raw_temp = self.rxdata[3] & 0x0F
            raw_temp <<= 8
            raw_temp += self.rxdata[4]
            raw_temp <<= 8
            raw_temp += self.rxdata[5]
            float_temp = float((raw_temp / 1048576.0 ) * 200.0 - 50.0)
            
        return [float_humid, float_temp]
