'''
Docstring for drivers.networkingNode

Manages REST API calls. 


'''

import network
import urequests
import time
import json

class NetworkingNode:

    def __init__(self, ssid, password, server_ip, port=5000):
        self.ssid = ssid
        self.password = password
        self.server_ip = server_ip
        self.port = port
        self.wlan = network.WLAN(network.STA_IF)

    # -----------------------------
    # WiFi Connection
    # -----------------------------
    def connect_wifi(self, timeout=15):
        if not self.wlan.active():
            self.wlan.active(True)

        if not self.wlan.isconnected():
            print("Connecting to WiFi...")
            self.wlan.connect(self.ssid, self.password)

            start_time = time.time()
            while not self.wlan.isconnected():
                if time.time() - start_time > timeout:
                    raise RuntimeError("WiFi connection timeout")
                time.sleep(1)

        print("WiFi connected:", self.wlan.ifconfig())

    def ensure_connection(self):
        if not self.wlan.isconnected():
            print("WiFi lost. Reconnecting...")
            self.connect_wifi()

    # -----------------------------
    # HTTP GET
    # -----------------------------
    def get_state(self):
        self.ensure_connection()

        url = f"http://{self.server_ip}:{self.port}/api/state"

        try:
            response = urequests.get(url)
            data = response.json()
            response.close()
            return data
        except Exception as e:
            print("GET error:", e)
            return None

    # -----------------------------
    # HTTP POST
    # -----------------------------
    def send_command(self, mode):
        self.ensure_connection()

        url = f"http://{self.server_ip}:{self.port}/api/command"
        payload = {"mode": mode}

        try:
            response = urequests.post(url, json=payload)
            response.close()
            return True
        except Exception as e:
            print("POST error:", e)
            return False