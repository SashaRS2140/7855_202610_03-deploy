import time
import threading

class CountupTimer:
    def __init__(self):
        self.lock = threading.Lock()
        self.start_time = None
        self.target_duration = 0  # seconds
        self.running = False
        self.elapsed_at_stop = 0

    def start(self):
        with self.lock:
            if not self.running:
                # Resume from where we stopped
                self.start_time = time.time() - self.elapsed_at_stop
                self.running = True

    def reset(self, seconds):
        with self.lock:
            self.target_duration = seconds
            self.start_time = time.time()
            self.elapsed_at_stop = 0

    def stop(self):
        with self.lock:
            if self.running and self.start_time:
                self.elapsed_at_stop = int(time.time() - self.start_time)
            self.running = False

    def get_elapsed(self):
        with self.lock:
            if self.running and self.start_time:
                return int(time.time() - self.start_time)
            # When stopped, return frozen elapsed time
            return self.elapsed_at_stop

    def get_target(self):
        with self.lock:
            return self.target_duration