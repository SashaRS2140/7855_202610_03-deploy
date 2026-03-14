'''
Docstring for drivers.networkingNode

Manages REST API calls. 


'''

import network
import urequests
import time
import json



def hex_to_rgbw(hex_color: str):
    """
    Convert HEX color (#RRGGBB) to RGBW.

    Parameters
    ----------
    hex_color : str
        Color string like "#ffaa00"

    Returns
    -------
    tuple
        (r, g, b, w) values from 0–255
    """

    # Convert HEX → RGB
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)

    # Extract white component
    w = min(r, g, b)

    # Remove white from RGB
    r -= w
    g -= w
    b -= w

    return r, g, b, w


class NetworkingNode:

    def __init__(self, ssid, password, server_ip, port=5000):
        self.ssid = ssid
        self.password = password
        self.server_ip = server_ip
        self.port = port
        self.wlan = network.WLAN(network.STA_IF)
        

    # WiFi Connection
    def connect_wifi(self, timeout=5):        
        # Turn on the WiFi interface if it's not already active
        if not self.wlan.active():
            self.wlan.active(True)

        # Only try to connect if we're not already connected
        if not self.wlan.isconnected():
            print("Connecting to WiFi...")
            self.wlan.connect(self.ssid, self.password)

            # Start a timer to enforce a connection timeout
            start_time = time.time()
            while not self.wlan.isconnected():
                # If we've waited longer than 'timeout' seconds, give up
                if time.time() - start_time > timeout:
                    self.wlan.active(False)  # turn off radio to save power
                    raise RuntimeError("WiFi connection timeout")
                time.sleep(1)
        # If we reach this point, we're connected
        print("WiFi connected:", self.wlan.ifconfig())

            # -------- SERVER CHECK --------
        url = f"http://{self.server_ip}:{self.port}/api/esp/config"

        try:
            response = urequests.get(url)
            response.close()
            print("Server reachable")

        except Exception:
            print("Server unreachable, disabling WiFi")
            self.wlan.active(False)
            raise RuntimeError("Server not reachable")
#  or not self.check_server()
    def ensure_connection(self):
        if not self.wlan.isconnected():
            print("offline mode")
            return False
        return True
    

    

    '''
    # LP5811 timing codes: [0h:0s, 1h:0.09s, 2h:0.18s, 3h:0.36s, 4h:0.54s, 5h:0.80s, 6h:1.07s, 7h:1.52s, 8h:2.06s, 9h:2.50s, Ah:3.04s, Bh:4.02s, Ch:5.01s, Dh:5.99s, Eh:7.06s, Fh:8.05s]

    Example for reset pull 
    Server: {
        "message": "Demo task reset",
        "task_name": "Demo", 
        "task_time": 600,
        "task_color": #ffaa00,
        "timing_patern": [minimum_intensity time,rise time,peak time,fall time],
        "alarm_type": "bell"
    }

    '''
    def get_state(self):

        if not self.ensure_connection():
            return None

        url = f"http://{self.server_ip}:{self.port}/api/esp/config"

        headers = {
            "Authorization": f"Bearer {self.token}"
        }

        try:
            response = urequests.get(url, headers=headers)
            data = response.json()
            response.close()

            # ---- REQUIRED FIELDS ----
            required_fields = [
                "task_name",
                "task_time",
                "task_color",
                "timing_pattern",
                "alarm_type"
            ]

            # ---- VALIDATE JSON ----
            for field in required_fields:
                if field not in data:
                    print("CONFIG FORMAT ERROR: missing field", field)
                    return None

            # If validation passes, return the JSON unchanged
            return data

        except Exception as e:
            print("GET error:", e)
            return None
            

    '''
    
    //example for posts but be made using device_id as key in header of json !!!!!!!!!!!        
    // on start command dabase utc starttime from firebase 
    // on stop cube sends elapsed time and it is stored in database
    Cube:{
        "task": "MEDITATION",
        "action": "START",
    }

    Cube:{
        "task": "MEDITATION",   
        "action": "STOP",
        "time_elapsed": 123124:
    }
    // Reset command is basically just an api call 
    Cube:{
        "action": "reset"
    }
    '''

    # HTTP POST occurs when buttons is pressed singleTap or doubleTap
    # The purpose of this is to save data into server.
    def send_command(self):

        if not self.ensure_connection():
            return False

        url = f"http://{self.server_ip}:{self.port}/api/esp/telemetry"

        headers = {
            "Authorization": f"Bearer {self.token}"
        }

        # ---------- PAYLOAD BASE ----------
        payload = {
            # "device_id": "cube_01"
        }

        # ---------- MODE HANDLING ----------

        if self.mode == "START":

            payload = {
                "task": self.task,
                "action": "START",
                "timestamp": time.time()
            }

        elif self.mode == "STOP":

            payload = {
                "task": self.task,
                "action": "STOP",
                "time_elapsed": self.time_elapsed
            }

        elif self.mode == "RESET":

            payload = {
                "action": "RESET"
            }

        else:
            print("Unknown mode:", self.mode)
            return False

        # ---------- SEND ----------
        try:
            response = urequests.post(url, json=payload, headers=headers)
            response.close()
            return True

        except Exception as e:
            print("POST error:", e)
            return False