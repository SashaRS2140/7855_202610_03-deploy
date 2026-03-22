from flask import Flask, request, jsonify

app = Flask(__name__)

# ---- server state ----
state = {
    "mode": "idle",
    "last_command": None
}

# ---- CONFIG (GET) ----
@app.route("/api/esp/config", methods=["GET"])
def get_config():
    # This must match what your ESP32 expects
    config = {
        "task_name": "Meditation",
        "task_time": 600,
        "task_color": "#ffaa00",
        "timing_pattern": [1, 2, 3, 4],
        "alarm_type": "bell"
    }

    return jsonify(config), 200


# ---- TELEMETRY (POST) ----
@app.route("/api/esp/telemetry", methods=["POST"])
def telemetry():
    data = request.get_json()

    if not data or "action" not in data:
        return jsonify({"error": "Invalid payload"}), 400

    action = data["action"]

    print("Received:", data)

    # ---- Handle actions ----
    if action == "START":
        state["mode"] = "running"
        state["last_command"] = data

    elif action == "STOP":
        state["mode"] = "stopped"
        state["last_command"] = data

    elif action == "RESET":
        state["mode"] = "idle"
        state["last_command"] = data

    else:
        return jsonify({"error": "Unknown action"}), 400

    return jsonify({
        "status": "ok",
        "state": state
    }), 200


# ---- RUN SERVER ----
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)