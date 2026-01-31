'''
python -m mpremote cp main.py :
python -m mpremote connect COM7 repl
python -m mpremote reset
'''




#then press reset or 
import time
from machine import ADC, I2C, Pin, PWM
from drivers.lp5811_ledDriver import LP5811 # uses custom I2C protocol

######### Initialization of peripherals #########

LP5811_ADDR = 0x6D
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
    try:
        # Send a zero-length write (just address + ACK check)
        i2c.writeto(LP5811_ADDR, b"")
        print("ACK from 0x%02X" % LP5811_ADDR)
        led.on()
    except OSError as e:
        print("NO ACK from 0x%02X" % LP5811_ADDR, e)
        led.off()

    time.sleep(1)