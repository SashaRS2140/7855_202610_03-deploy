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
from drivers.piezoElectric import *
from drivers.pomodoroTimer import *
from drivers.alarm import *


######### Initialization of peripherals #########

def on_done(alarm, lp):
    print("Timer finished")
    alarm.bell()
    lp.stop_cmd() 


def on_reminder():
    print("Reminder!")

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

    piezo = PiezoButton(pin=34)



    timer = PomodoroTimer(
        on_session_complete=lambda: on_done(alarm,lp),
        on_reminder=on_reminder
    )

    # -------------------------------
    # Configure timers
    # -------------------------------


    # timer.set_reminder(3) # optional: reminder every 3 seconds
    alarm = Alarm(speaker_pin=18)





    # lp.init_manual()
    lp.init_auto()  # Start auto mode with default breathing pattern
    lp.led_all_breathing([255,0,0,0])
    # lp.write_reg(UPDATE_CMD_REG , UPDATE_CMD_VALUE)  # Enable device
    while True:
        # lp.fade_leds_manual([255, 0, 0 , 0], 4000)   # Fade to white in 5s
        # lp.fade_leds_manual([255, 0, 0 , 0], 4000)   # Fade to white in 5s
        # lp.fade_leds_manual([0, 0, 0, 0], 4000)   # Fade out in 2s
        # lp.fade_leds_manual([0, 0, 0, 0], 4000)   # Fade out in 2s
        timer.process()     # MUST be called regularly

        press = piezo.buttonPress()
        if press == 1:
            print("Single tap")
            timer.set_time(15 )   
            timer.start()
            lp.start_cmd()

        elif press == 2:
            print("Double tap")

if __name__ == "__main__":
    main()