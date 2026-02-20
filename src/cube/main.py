# main.py (MicroPython / ESP32)

import time
from machine import ADC, I2C, Pin, PWM

import secrets  # secrets.WIFI_SSID, WIFI_PASSWORD, SERVER_IP, SERVER_PORT

from drivers.lp5811_ledDriver import LP5811
from drivers.piezoElectric import PiezoButton
from drivers.pomodoroTimer import PomodoroTimer
from drivers.alarm import Alarm
from drivers.networkingNode import NetworkingNode  # adjust import to your actual path/name


class CubeController:
    def __init__(self):
        # ---- Constants ----
        self.LP5811_ADDR = 0x6D

        # ---- Hardware ----
        self.onboard_led = Pin(2, Pin.OUT)

        # ADC (if you still want it; PiezoButton already uses pin=34 in your code)
        self.adc = ADC(Pin(34))
        self.adc.atten(ADC.ATTN_11DB)

        # I2C + LP5811
        self.i2c = I2C(0, scl=Pin(22), sda=Pin(21))
        self.lp = LP5811(self.i2c)

        # PWM outputs (optional; Alarm may create its own PWM, but leaving these here if you use them elsewhere)
        self.speaker_pwm = PWM(Pin(18), freq=1000)
        self.vibration_pwm = PWM(Pin(19), freq=1000)

        # Inputs / helpers
        self.piezo = PiezoButton(pin=34)
        self.alarm = Alarm(speaker_pin=18)

        # Timer (callbacks point to controller methods)
        self.timer = PomodoroTimer(
            on_session_complete=self.on_session_complete,
            on_reminder=self.on_reminder,
        )

        # Networking
        self.network = NetworkingNode(
            secrets.WIFI_SSID,
            secrets.WIFI_PASSWORD,
            secrets.SERVER_IP,
            secrets.SERVER_PORT,
        )

    # ---------- Callbacks ----------
    def on_session_complete(self):
        print("Timer finished")
        self.alarm.bell()
        self.lp.stop_cmd()

    def on_reminder(self):
        print("Reminder!")

    # ---------- Setup ----------
    def init_lp5811(self) -> bool:
        if not self.lp.ping():
            print("LP5811 not detected (NACK)")
            return False
        print("✅ LP5811 detected (ACK)")
        return True

    def init_network(self):
        self.network.connect_wifi()
        try:
            state = self.network.get_state()
            print(state)
        except Exception as e:
            print("Failed to fetch server state:", e)

    # ---------- Behavior ----------
    def handle_single_tap(self):
        print("Single tap")

        self.timer.set_time(20 * 60)
        self.timer.start()

        # LED breathing
        self.lp.init_auto()
        self.lp.led_all_breathing([255, 0, 0, 0])
        self.lp.start_cmd()

    def handle_double_tap(self):
        print("Double tap")
        # add whatever you want here

    # ---------- Main loop ----------
    def run(self):
        print("main.py running")

        if not self.init_lp5811():
            return

        self.init_network()

        while True:
            self.timer.process()  # MUST be called regularly

            press = self.piezo.buttonPress()
            if press == 1:
                self.handle_single_tap()
            elif press == 2:
                self.handle_double_tap()

            # small yield (optional)
            time.sleep_ms(5)


def main():
    controller = CubeController()
    controller.run()


if __name__ == "__main__":
    main()