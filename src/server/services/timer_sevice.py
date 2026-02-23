import time
import threading

class CountupTimer:
    def __init__(self):
        self.lock = threading.Lock()
        self.start_time = None
        self.target_duration = 0  # seconds
        self.running = False

    def start(self):
        with self.lock:
            if not self.running:
                self.start_time = time.time()
                self.running = True

    def reset(self, seconds):
        with self.lock:
            self.target_duration = seconds
            self.start_time = time.time()

    def stop(self):
        with self.lock:
            self.running = False

    def get_elapsed(self):
        with self.lock:
            if not self.running or not self.start_time:
                return 0
            return int(time.time() - self.start_time)

    def get_target(self):
        with self.lock:
            return self.target_duration
