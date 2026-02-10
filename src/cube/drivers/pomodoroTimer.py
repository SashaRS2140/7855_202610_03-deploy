'''
Docstring for drivers.pomodoroTimer


Features for pomodoro timer

-set time
-start timer
-pause timer
-add time
-reset timer
-probably needs some sort of interupt or callback function

Probably set the timer to go up, then trigger when  = setTime.


There will be 2 timers in this class. 
1. Session duration <-- counts up. And triggers interrupt upon reaching set time.
2. Reminder duration ( should be programmed so be completely programmable)

'''


from machine import Timer


class PomodoroTimer:
    """
    Pomodoro Timer using ESP32 hardware timers (MicroPython).

    Features:
    - Set session time (counts UP)
    - Start / pause / reset
    - Add time dynamically
    - Session complete callback
    - Reminder timer (programmable, repeating or one-shot)
    """

    def __init__(self,
                 on_session_complete=None,
                 on_reminder=None):
        # ---- Callbacks (run in main context, NOT ISR) ----
        self.on_session_complete = on_session_complete
        self.on_reminder = on_reminder

        # ---- Session timer state ----
        self.set_time_ms = 0
        self.session_elapsed_ms = 0
        self.session_running = False
        self.session_done = False

        # ---- Reminder timer state ----
        self.reminder_interval_ms = None
        self.reminder_elapsed_ms = 0
        self.reminder_enabled = False
        self.reminder_repeat = True

        # ---- ISR flags ----
        self._session_tick = False
        self._reminder_tick = False

        # ---- Hardware timers ----
        self._session_timer = Timer(0)
        self._reminder_timer = Timer(1)

    # ==================================================
    # Session control
    # ==================================================

    def set_time(self, seconds: int):
        """Set session duration (seconds)."""
        self.set_time_ms = seconds * 1000
        self.session_elapsed_ms = 0
        self.session_done = False

    def start(self):
        """Start or resume the session timer."""
        if self.set_time_ms <= 0:
            raise ValueError("Call set_time() before start()")

        self.session_running = True
        self._start_session_timer()

    def pause(self):
        """Pause session timer."""
        self.session_running = False
        self._session_timer.deinit()

    def reset(self):
        """Reset session timer."""
        self.pause()
        self.session_elapsed_ms = 0
        self.session_done = False

    def add_time(self, seconds: int):
        """Add time to session duration."""
        self.set_time_ms += seconds * 1000

    # ==================================================
    # Reminder control
    # ==================================================

    def set_reminder(self, interval_seconds: int, repeat: bool = True):
        """
        Configure reminder timer.
        interval_seconds: reminder period
        repeat: True = periodic, False = one-shot
        """
        self.reminder_interval_ms = interval_seconds * 1000
        self.reminder_elapsed_ms = 0
        self.reminder_enabled = True
        self.reminder_repeat = repeat
        self._start_reminder_timer()

    def disable_reminder(self):
        self.reminder_enabled = False
        self._reminder_timer.deinit()

    # ==================================================
    # Hardware timer setup (ISR-safe)
    # ==================================================

    def _start_session_timer(self):
        self._session_timer.init(
            period=1000,
            mode=Timer.PERIODIC,
            callback=self._session_timer_cb
        )

    def _start_reminder_timer(self):
        self._reminder_timer.init(
            period=1000,
            mode=Timer.PERIODIC,
            callback=self._reminder_timer_cb
        )

    # ==================================================
    # Timer callbacks (ISR CONTEXT — KEEP MINIMAL)
    # ==================================================

    def _session_timer_cb(self, timer):
        self._session_tick = True

    def _reminder_timer_cb(self, timer):
        self._reminder_tick = True

    # ==================================================
    # Main processing (call from main loop)
    # ==================================================

    def process(self):
        """
        Handle timer ticks.
        Call this regularly from the main loop.
        """

        # ---- Session timer ----
        if self._session_tick:
            self._session_tick = False

            if self.session_running and not self.session_done:
                self.session_elapsed_ms += 1000

                if self.session_elapsed_ms >= self.set_time_ms:
                    self.session_done = True
                    self.session_running = False
                    self._session_timer.deinit()

                    if self.on_session_complete:
                        self.on_session_complete()

        # ---- Reminder timer ----
        if self._reminder_tick:
            self._reminder_tick = False

            if self.reminder_enabled and self.reminder_interval_ms:
                self.reminder_elapsed_ms += 1000

                if self.reminder_elapsed_ms >= self.reminder_interval_ms:
                    if self.on_reminder:
                        self.on_reminder()

                    if self.reminder_repeat:
                        self.reminder_elapsed_ms = 0
                    else:
                        self.disable_reminder()
