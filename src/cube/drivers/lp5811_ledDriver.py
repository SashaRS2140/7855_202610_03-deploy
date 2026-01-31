"""
Author: Parry
Date: Jan 29, 2026

LP5811 LED Driver — Custom I2C Interface
---------------------------------------

This module implements I2C communication for the Texas Instruments LP5811
LED driver.

The LP5811 does NOT use a standard 7-bit I2C register addressing scheme.
Instead, it implements a CUSTOM I2C protocol with a split address format.

ADDRESSING SCHEME
-----------------
Each I2C transaction uses two address bytes composed of:

- 5-bit device (chip) address
- 9-bit register address
- 1-bit R/W flag (0 = write, 1 = read)

Address Byte 1 ( 5-bit device (chip) address + upper 2 bits of register address + R/W flag )
Address Byte 2 ( lower 7 bits of register address )

This driver manually constructs the address bytes and therefore does NOT
use standard I2C memory helpers such as `writeto_mem()` or `readfrom_mem()`.

SOURCE
------
Code adapted from Texas Instruments LP5811 reference implementation:
https://www.ti.com/product/LP5811
"""


from machine import I2C

class LP5811:
    def __init__(self, i2c: I2C, address=0x50):
        self.i2c = i2c
        self.address = address
        
    def _write_reg(self, reg, value):
        self.i2c.writeto_mem(self.address, reg, bytes([value]))

    def _read_reg(self, reg):
        return self.i2c.readfrom_mem(self.address, reg, 1)[0]
    
    def ping(self):
        try:
            self._read_reg(0x00)
            return True
        except OSError:
            return False
