# main.py (MicroPython / ESP32)
# .\push.ps1
import time
from machine import ADC, I2C, Pin, PWM

import secrets  # secrets.WIFI_SSID, WIFI_PASSWORD, SERVER_IP, SERVER_PORT

from drivers.lp5811_ledDriver import LP5811
from drivers.piezoElectric import PiezoButton
from drivers.pomodoroTimer import PomodoroTimer
from drivers.alarm import Alarm
from drivers.networkingNode import NetworkingNode  # adjust import to your actual path/name

MODE_STOP   = 0
MODE_RUNNING = 1
MODE_CONFIG  = 2
MODE_ERROR   = 3

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

        # PWM outputs
        self.speaker_pwm = PWM(Pin(18), freq=1000)
        self.vibration_pwm = PWM(Pin(19), freq=1000)

        # Inputs
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
        # THE DIFFERENT MODES ARE PAUSE and RUNNING
        self.task = "Nothing"
        self.mode = MODE_RUNNING
        self.stopWatchPresetTime = 20*60   # 20 minutes in seconds

        self.bearerToken = "supersecretbearertoken"  

    def error_animation(self):
        print("Error mode: flashing red")
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
        try:
            self.network.connect_wifi()
        except Exception as e:
            print("Failed to connect to WiFi:", e)
        try:
            state = self.network.get_state()
            print(state)
        except Exception as e:
            print("Failed to fetch server state:", e)

    # ---------- Upon single tap, will toggle mode and send respective commands to server----------
    def handle_single_tap(self):
        print("Single tap")
        self.toggle_mode()
        json_payload = {}
        if self.mode == MODE_RUNNING:# then STOP
            # JSON payload upon stopping
            # Cube:{
            #     "task": "MEDITATION",
            #     "action": "STOP",
            #     "time_elapsed": 123124:
            # }
            json_payload = {
                "task": self.task,
                "action": "STOP",
                "time_elapsed": self.timer.session_elapsed_ms /1000 # convert ms to seconds
            }
            self.lp.stop_cmd()
            self.timer.pause()
        elif self.mode == MODE_STOP: # then START
            # JSON payload upon starting
            # Cube:{
            #     "task": "MEDITATION",
            #     "action": "START",
            # }
            json_payload = {
                "task": self.task,
                "action": "START",
            }
            # LED breathing
            self.timer.set_time(self.stopWatchPresetTime)
            self.timer.start()
            self.lp.init_auto()
            self.lp.led_all_breathing([255, 0, 0, 0])
            self.lp.start_cmd()

        # Send REST command at end so it does not stop animation. 

        #    def send_command(self, task , mode, time_elapsed=None):
        success = self.network.send_command(json_payload)
        if success:
            print(str(self.mode) + " Command sent successfully")
        else:
            self.error_animation()

    def handle_double_tap(self):
        # Send REST command

        self.lp.stop_cmd()
        self.timer.pause()
        # JSON payload upon reset
        # Cube:{
        #     "task": "Meditation",      
        #     "action": "reset"
        # }
        json_payload = {
            "task": self.task,
            "action": "RESET",
        }
        success = self.network.send_command(json_payload)
        if success:
            print("Command sent successfully")
        else:
            print("Failed to send command")

    def toggle_mode(self):
        if self.mode == MODE_STOP:
            self.mode = MODE_RUNNING
        else:
            self.mode = MODE_STOP


    # ---------- Main loop ----------
    def run(self):
        print("main.py running")

        if not self.init_lp5811():
            return

        self.init_network()

        while True:
            self.timer.process() 
            press = self.piezo.buttonPress()
            if press == 1:
                self.handle_single_tap()
            elif press == 2:
                self.handle_double_tap()

            # time.sleep_ms(5)

def main():
    controller = CubeController()
    controller.run()

if __name__ == "__main__":
    main()