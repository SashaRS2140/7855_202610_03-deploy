"""
drivers.piezoElectric

Analog piezo / vibration button using ADC polling.

Features:
- Baseline tracking
- Hysteresis thresholds
- Debounce / settle logic
- Single-tap and double-tap detection

buttonPress() returns:
    0 → no press
    1 → single press
    2 → double press
"""

import time
from machine import ADC, Pin

class PiezoButton:
    def __init__(
        self,
        pin: int,
        fs_hz: int = 1000,
        threshold_high: int = 400,
        threshold_low: int = 50,
        baseline_alpha: float = 0.5,
        settle_ms: int = 30,
        double_tap_ms: int = 1000
    ):
        # ADC setup
        self.adc = ADC(Pin(pin))
        self.adc.atten(ADC.ATTN_11DB)
        self.adc.width(ADC.WIDTH_12BIT)

        # Timing
        self.fs_hz = fs_hz
        self.dt_ms = 1000 // fs_hz
        self.settle_ms = settle_ms
        self.double_tap_ms = double_tap_ms

        # Thresholds
        self.threshold_high = threshold_high
        self.threshold_low = threshold_low
        self.alpha = baseline_alpha

        # State
        self.baseline = self.adc.read()
        self.state = 0  # 0=IDLE, 1=ACTIVE, 2=WAIT_SETTLE
        self.quiet_since = 0 

        # Tap tracking
        self.tap_count = 0
        self.doubleTap = 0
        self.last_double_tap_time = 0

    def buttonPress(self) -> int:
        sample = self.adc.read()

        # Baseline tracking. LOW PASS FILTER. REMOVES NOISE AND DRIFT
        self.baseline = (1 - self.alpha) * self.baseline + self.alpha * sample
        delta = abs(sample - self.baseline) # DELTA IS BIG IF THERE'S A SUDDEN JUMP IN VALUE


        # print(self.state, delta)
        # print(f"Sample: {sample}, Baseline: {self.baseline:.2f}, Delta: {delta:.2f}, State: {self.state}")
        now = time.ticks_ms()
        result = 0

        # ---------- STATE MACHINE ----------
        if self.state == 0:  # IDLE
            if delta > self.threshold_high:
                self.state = 1  # tap started

        elif self.state == 1:  # ACTIVE (waiting for release)
            if delta < self.threshold_low:
                self.quiet_since = now
                self.state = 2  # wait for settle

        elif self.state == 2:  # WAIT_SETTLE ( wait for signal to settle down)
            if delta < self.threshold_low:
                diffTime = time.ticks_diff(now, self.quiet_since)
                if diffTime > self.settle_ms:
                    print(str(self.doubleTap) + " taps, " + str(diffTime) + " ms\n")
                    self.state = 0
                    result = 1  # SINGLE TAP
                    self.doubleTap += 1 
                    print("Double Tap Count: " + str(self.doubleTap))
                    self.last_double_tap_time = now  #start timer for double tap
            else:
                # vibration still happening
                self.quiet_since = now
        # ----------------------------------

        #for double tap detection
        if time.ticks_diff(now, self.last_double_tap_time) >= self.double_tap_ms:
            if self.doubleTap >= 2:
                print("Double Tap Detected!@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@" + str(self.doubleTap) )
                result = 2  # DOUBLE TAP
            self.doubleTap = 0  # reset tap count if too much time has passed
            


        time.sleep_ms(self.dt_ms)
        return result
