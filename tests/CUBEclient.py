import tkinter as tk
from tkinter import scrolledtext
import requests
import threading
import json

SERVER_URL = "http://127.0.0.1:5000/api/task/control"

class CubeSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("The CUBE Simulator")

        # Track local state: "stopped", "running", "paused"
        self.state = "stopped"

        # ===== Title Banner =====
        banner = tk.Label(
            root,
            text="The CUBE Simulator",
            font=("Helvetica", 20, "bold"),
            pady=10
        )
        banner.pack()

        # ===== Time Input (Minutes + Seconds) =====
        input_frame = tk.Frame(root)
        input_frame.pack(pady=5)

        tk.Label(input_frame, text="Minutes:").grid(row=0, column=0, padx=5)
        self.minutes_entry = tk.Entry(input_frame, width=5)
        self.minutes_entry.grid(row=0, column=1, padx=5)

        tk.Label(input_frame, text="Seconds:").grid(row=0, column=2, padx=5)
        self.seconds_entry = tk.Entry(input_frame, width=5)
        self.seconds_entry.grid(row=0, column=3, padx=5)

        # ===== Buttons =====
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        self.start_button = tk.Button(button_frame, text="Start", width=10, command=self.on_start)
        self.start_button.grid(row=0, column=0, padx=5)

        self.pause_button = tk.Button(button_frame, text="Pause", width=10, command=self.on_pause)
        self.pause_button.grid(row=0, column=1, padx=5)

        self.stop_button = tk.Button(button_frame, text="Stop", width=10, command=self.on_stop)
        self.stop_button.grid(row=0, column=2, padx=5)

        # ===== Display Window =====
        self.display = scrolledtext.ScrolledText(root, width=60, height=15)
        self.display.pack(pady=10)

        self.log("Client ready.")

    # ---------- Button Handlers ----------

    def on_start(self):
        if self.state == "paused":
            payload = {"action": "resume"}
            self.send_request(payload)
            self.state = "running"
        else:
            # Handle empty fields
            minutes_str = self.minutes_entry.get().strip()
            seconds_str = self.seconds_entry.get().strip()

            minutes = 0
            seconds = 0

            if minutes_str:
                if not minutes_str.isdigit():
                    self.log("Minutes must be a number between 0-60.")
                    return
                minutes = int(minutes_str)
                if not (0 <= minutes <= 60):
                    self.log("Minutes must be between 0 and 60.")
                    return

            if seconds_str:
                if not seconds_str.isdigit():
                    self.log("Seconds must be a number between 0-60.")
                    return
                seconds = int(seconds_str)
                if not (0 <= seconds <= 60):
                    self.log("Seconds must be between 0 and 60.")
                    return

            if minutes == 0 and seconds == 0:
                self.log("Please enter a non-zero time.")
                return

            payload = {
                "action": "start",
                "minutes": minutes,
                "seconds": seconds
            }
            self.send_request(payload)
            self.state = "running"

    def on_pause(self):
        if self.state == "running":
            payload = {"action": "pause"}
            self.send_request(payload)
            self.state = "paused"
        else:
            self.log("Cannot pause: Timer not running.")

    def on_stop(self):
        payload = {"action": "stop"}
        self.send_request(payload)
        self.state = "stopped"

    # ---------- Networking ----------

    def send_request(self, payload):
        threading.Thread(target=self._request_worker, args=(payload,), daemon=True).start()

    def _request_worker(self, payload):
        try:
            response = requests.post(SERVER_URL, json=payload)
            if response.headers.get("Content-Type", "").startswith("application/json"):
                data = response.json()
                self.log(f"Server: {json.dumps(data)}")
            else:
                self.log(f"Server returned non-JSON: {response.text}")
        except Exception as e:
            self.log(f"Request error: {e}")

    # ---------- Display ----------

    def log(self, message):
        self.display.insert(tk.END, message + "\n")
        self.display.see(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = CubeSimulatorGUI(root)
    root.mainloop()
