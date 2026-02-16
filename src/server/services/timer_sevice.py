import time
import threading

class CountdownTimer:
    def __init__(self):
        self.lock = threading.Lock()
        self.duration = 0
        self.end_time = None
        self.paused = True
        self.remaining = 0

    def start(self, seconds):
        with self.lock:
            self.duration = seconds
            self.end_time = time.time() + seconds
            self.paused = False

    def pause(self):
        with self.lock:
            if not self.paused and self.end_time:
                self.remaining = max(0, self.end_time - time.time())
                self.paused = True

    def resume(self):
        with self.lock:
            if self.paused:
                self.end_time = time.time() + self.remaining
                self.paused = False

    def stop(self):
        with self.lock:
            self.paused = True
            self.end_time = None
            self.remaining = 0

    def get_remaining(self):
        with self.lock:
            if self.paused:
                return int(self.remaining)
            if self.end_time:
                return max(0, int(self.end_time - time.time()))
            return 0
