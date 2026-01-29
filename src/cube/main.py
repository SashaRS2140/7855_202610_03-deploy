#python -m mpremote cp main.py :
#python -m mpremote connect COM7 repl
#python -m mpremote reset

#then press reset or 
import time
from machine import ADC, I2C, Pin, PWM

from drivers.lp5811_ledDriver import LP5811 # uses custom I2C protocol

#Initialization of peripherals

# ADC
adc = ADC(Pin(34))
adc.atten(ADC.ATTN_11DB)

# I2C
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
print("I2C devices:", i2c.scan())

# PWM
speakerPwm = PWM(Pin(18), freq=1000)
vibrationPwm = PWM(Pin(19), freq=1000)

print("main.py running")

led = Pin(2, Pin.OUT)

while True:
    led.toggle()
    time.sleep(1)

