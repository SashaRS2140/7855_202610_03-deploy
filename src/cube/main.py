'''
python -m mpremote cp main.py :
python -m mpremote connect COM7 repl
python -m mpremote reset

run the following in powershell extension to compile and upload everything.
.\push.ps1
'''


#then press reset or 
import time
from machine import ADC, I2C, Pin, PWM
from drivers.lp5811_ledDriver import * # uses custom I2C protocol

######### Initialization of peripherals #########

def main():
    LP5811_ADDR = 0x6D
    # ADC
    adc = ADC(Pin(34))
    adc.atten(ADC.ATTN_11DB)

    # I2C
    i2c = I2C(0, scl=Pin(22), sda=Pin(21))
    # print("I2C devices:", i2c.scan())

    lp = LP5811(i2c)
    if not lp.ping():
        print("LP5811 not detected (NACK)")
        return
    print("✅ LP5811 detected (ACK)")

    # PWM
    speakerPwm = PWM(Pin(18), freq=1000)
    vibrationPwm = PWM(Pin(19), freq=1000)

    print("main.py running")

    onboardLed = Pin(2, Pin.OUT)


    lp.init_manual()
    lp.write_reg(UPDATE_CMD_REG , UPDATE_CMD_VALUE)  # Enable device
    while True:
        lp.fade_leds_manual([255, 0, 0 , 0], 2000)   # Fade to red in 2s
        lp.fade_leds_manual([126, 0, 0, 0], 2000)   # Fade to red in 2s
        lp.fade_leds_manual([0, 0, 0, 0], 2000)   # Fade to red in 2s


        # FORCE outputs OFF
        # for i in range(3):
        #     lp.write_reg(MANUAL_PWM_START + i, 0)

        # lp.fade_leds_manual([0, 255, 0], 500)    # Fade to green in 0.5s
        # lp.fade_leds_manual([0, 0, 255], 2000)   # Fade to blue in 2s
        # lp.fade_leds_manual([255, 255, 255], 1500)  # Fade to white
        # lp.fade_leds_manual([255, 0, 0], 1000)  # Fade to red over 1 second
        # try:
        #     # Send a zero-length write (just address + ACK check)
        #     i2c.writeto(LP5811_ADDR, b"")
        #     print("ACK from 0x%02X" % LP5811_ADDR)
        #     onboardLed.on()
        # except OSError as e:
        #     print("NO ACK from 0x%02X" % LP5811_ADDR, e)
        #     onboardLed.off()

        # time.sleep(1)

if __name__ == "__main__":
    main()