from flask import Flask, request, jsonify

app = Flask(__name__)

# ---- server state (in-memory) ----
state = {
    "mode": "idle"
}

# ---- POST: write state ---- #
@app.route("/api/command", methods=["POST"])
def command():
    data = request.get_json()

    if not data or "mode" not in data:
        return jsonify({"error": "Invalid command"}), 400

    state["mode"] = data["mode"]
    print("Mode set to:", state["mode"])

    return jsonify({
        "status": "ok",
        "state": state
    }), 200


# ---- GET: read state ----
@app.route("/api/state", methods=["GET"])
def get_state():
    return jsonify(state), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

