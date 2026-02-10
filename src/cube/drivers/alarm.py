'''
Docstring for drivers.alarm


This class is in charge of setting alarms such as potentially 
vibration motors, or speakers
'''



from machine import PWM, Pin
from time import sleep_ms


class Alarm:
    """
    Alarm driver for speaker (and optional vibration motor).

    Responsibilities:
    - Generate audible alarm patterns using PWM
    - No timing logic (external controller decides WHEN)
    """

    def __init__(self, speaker_pin=18, freq=1000):
        self.speaker = PWM(Pin(speaker_pin))
        self.speaker.freq(freq)
        self.speaker.duty_u16(0)  # silent by default

    # ============================================
    # Low-level control
    # ============================================

    def _on(self, duty=30000):
        self.speaker.duty_u16(duty)

    def _off(self):
        self.speaker.duty_u16(0)

    def stop(self):
        """Immediately silence the speaker."""
        self._off()

    # ============================================
    # Alarm patterns
    # ============================================

    def beep(self, duration_ms=200, duty=30000):
        """Single short beep."""
        self._on(duty)
        sleep_ms(duration_ms)
        self._off()

    def tick_tock(self, ticks=6):
        """
        Soft mechanical clock tick
        """
        for _ in range(ticks):
            self.speaker.freq(800)
            self._on(18000)
            sleep_ms(40)
            self._off()
            sleep_ms(600)


    def bell(self):

        self.speaker.freq(250)

        duty = 20000          # initial amplitude
        decay = 0.5          # exponential decay factor (smaller = faster fade)

        self._on(duty)
        sleep_ms(60)         # soft strike

        while duty > 2000:
            duty = int(duty * decay)
            self.speaker.duty_u16(duty)
            sleep_ms(10)

        self._off()