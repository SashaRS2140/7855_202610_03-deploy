class CubeInterfaceService:
    """
    Corresponds to 'Cube Interface Service' in the architecture.
    Handles logic for ESP32 'Tx/Rx data/cmds'.
    """
    def __init__(self):
        # In memory state for the Cube (or save to DB if needed)
        self.cube_state = {"status": "idle", "led_color": "#00FF00"}

    def process_telemetry(self, data):
        """Receive data from ESP32."""
        print(f"Received from ESP32: {data}")
        # Here you would call repository to log session data if needed
        return {"command": "continue"}

    def get_config(self):
        """Send parameters to ESP32."""
        return self.cube_state