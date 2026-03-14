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
    Example for reset pull 
    Server: {
        "message": "Demo task reset",
        "task_name": "Demo", 
        "task_time": 600,
        "task_color": #ffaa00,
        "r_patern": [minimum_intensity time,rise time,peak time,fall time],
        "g_patern": [5,3,3,4],
        "b_patern": [5,3,3,4],
        "w_patern": [5,3,3,4],
        "alarm_type": "bell"
    }

    '''
    def get_state(self):
        if not self.ensure_connection():
            return None
        url = f"http://{self.server_ip}:{self.port}/api/esp/config"

        try:
            response = urequests.get(url)
            data = response.json()
            response.close()

            # ---- TASK ----
            task = data.get("task", {})
            preset_time = task.get("preset_time_sec", 600)
            self.timer.set_task(
                task.get("name", "Default"),
                preset_time
            )

            # ---- LED ----
            led_block = data.get("led", {})
            channels = led_block.get("channels", {})

            for channel_name, cfg in channels.items():
                pwm_percent = cfg.get("max_pwm_percent", 100)
                anim = cfg.get("animation", {})

                self.led.configure_channel(
                    channel_name=channel_name,
                    pwm_percent=pwm_percent,
                    t1_code=anim.get("t1_code", 0),
                    t2_code=anim.get("t2_code", 0),
                    t3_code=anim.get("t3_code", 0),
                    t4_code=anim.get("t4_code", 0)
                )

            # ---- RETURN ALARM CONFIG ONLY ----
            alarm_config = {
                "alarm1": data.get("alarm1", {}),
                "alarm2": data.get("alarm2", {})
            }

            return alarm_config

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
    def send_command(self, command, timeElapsed=-1, presetTime=-1, task="Meditation"):

        if not self.ensure_connection():
            return False
        
        url = f"http://{self.server_ip}:{self.port}/api/esp/telemetry"

        payload = {
            "device_id": "cube_01",
            "task": task,
            "COMMAND": command,
            "timestamp": time.time(),
            "timeElapsed": timeElapsed,
            "preset time": presetTime
        }

        try:
            response = urequests.post(url, json=payload)
            response.close()
            return True

        except Exception as e:
            print("POST error:", e)
            return False