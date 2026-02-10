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
        baseline_alpha: float = 0.01,
        settle_ms: int = 400,
        double_tap_ms: int = 300,
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
        self.last_tap_time = 0
        self.tap_count = 0

    def buttonPress(self) -> int:
        """
        Poll ADC once.

        Returns:
            0 → no press
            1 → single press
            2 → double press
        """
        sample = self.adc.read()

        # Baseline tracking
        self.baseline = (1 - self.alpha) * self.baseline + self.alpha * sample
        delta = abs(sample - self.baseline)

        now = time.ticks_ms()
        result = 0

        # ---------- STATE MACHINE ----------
        if self.state == 0:  # IDLE
            if delta > self.threshold_high:
                self.state = 1

        elif self.state == 1:  # ACTIVE
            if delta < self.threshold_low:
                # Tap detected
                if time.ticks_diff(now, self.last_tap_time) < self.double_tap_ms:
                    result = 2
                    self.tap_count = 0
                else:
                    result = 1
                    self.tap_count = 1

                self.last_tap_time = now
                self.quiet_since = now
                self.state = 2

        elif self.state == 2:  # WAIT_SETTLE
            if delta < self.threshold_low:
                if time.ticks_diff(now, self.quiet_since) > self.settle_ms:
                    self.state = 0
            else:
                self.quiet_since = now
        # ----------------------------------

        time.sleep_ms(self.dt_ms)
        return result
