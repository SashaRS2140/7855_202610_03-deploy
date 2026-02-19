from flask import Blueprint, jsonify, request, current_app, session
from bcrypt import hashpw, checkpw, gensalt

api_bp = Blueprint('api', __name__)


def get_session_service():
    """Helper to access the service layer."""
    return current_app.session_service


def get_hw_service():
    return current_app.hw_service

def get_timer_service():
    return current_app.timer


##########################################################################
###                        CUBE REST API                               ###
##########################################################################

@api_bp.route("/esp/telemetry", methods=["POST"])
def receive_telemetry():
    """Endpoint for ESP32 to send button presses/sensor data."""
    data = request.get_json()
    response = get_hw_service().process_telemetry(data)
    return jsonify(response)


@api_bp.route("/esp/config", methods=["GET"])
def get_config():
    """Endpoint for ESP32 to fetch settings."""
    return jsonify(get_hw_service().get_config())

@api_bp.route("/task/control", methods=["POST"])
def task_control():
    timer = get_timer_service()
    sess_svc = get_session_service()

    if not request.is_json:
        return jsonify({"error": "JSON required"}), 415

    data = request.get_json()
    cube_uuid = data.get("cube_uuid")
    username = cube_uuid  # treat cube as session owner for now

    action = data.get("action")
    elapsed_time = data.get("elapsed_seconds")

    current_task = sess_svc.get_current_task(username)
    if not current_task:
        return jsonify({"error": "Current task not set"}), 400

    task_data = sess_svc.get_task_preset(username, current_task)
    task_time = task_data.get("task_time")
    tt_min = task_time // 60
    tt_sec = task_time % 60

    if action == "start":
        timer.start()
        return jsonify({"message": f"{current_task} task started"}), 200

    if action == "stop":
        timer.stop()
        sess_svc.save_session(username, current_task, elapsed_time)
        if elapsed_time <= task_time:
            min = elapsed_time // 60
            sec = elapsed_time % 60
            return jsonify({"message": f"{current_task} task stopped. "
                                       f"{min}m:{sec}s of session time logged."
                            }), 200
        else:
            extra_time = elapsed_time - task_time
            min = extra_time // 60
            sec = extra_time % 60
            return jsonify({"message": f"{current_task} task stopped. "
                                       f"{tt_min}m:{tt_sec}s of session time + "
                                       f"{min}m:{sec}s of extra session time logged."
                            }), 200

    if action == "reset":
        timer.reset(task_time)
        return jsonify({"message": f"{current_task} task reset",
                        "task_name": current_task,
                        "task_time": task_time
                        }), 200

    return jsonify({"error": "Invalid action"}), 400


##########################################################################
###                             REST API                               ###
##########################################################################

@api_bp.route("/profile", methods=["GET", "POST", "DELETE"])
def api_profile():
    svc = get_session_service()

    # Check authentication
    username = session.get("username")
    if not username:
        return jsonify({"error": "Unauthorized"}), 401

    if request.method == "GET":
        # Return the current user's profile as JSON
        profile_data = svc.get_profile(username)
        if not profile_data:
            return jsonify({"error": "Profile not found"}), 404
        return jsonify({
            "username": profile_data.get("username"),
            "profile": profile_data.get("profile"),
            "presets": profile_data.get("presets"),
            "current task": profile_data.get("current_task"),
        }), 200

    if request.method == "POST":
        # Check Content-Type header
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 415

        # Parse JSON payload
        try:
            data = request.get_json()
        except Exception:
            return jsonify({"error": "Invalid JSON"}), 400

        # Validate the data
        error = svc.validate_profile(data)
        if error:
            return jsonify({"error": error}), 400

        # Valid -> normalize and save
        normalized_profile = svc.normalize_profile(data)
        svc.save_profile(username, normalized_profile)

        return jsonify({
            "message": "Profile updated successfully",
            "profile": normalized_profile
        }), 200

    if request.method == "DELETE":
        if not svc.get_profile(username):
            return jsonify({"error": "Profile not found"}), 404

        svc.delete_profile(username)
        return jsonify({"message": "Profile deleted successfully"}), 200
    return None


@api_bp.route("/user", methods=["GET", "POST", "DELETE"])
def api_user():
    svc = get_session_service()

    username = session.get("username")

    if request.method == "GET":
        if not username:
            return jsonify({"message": "No user logged in"}), 200
        return jsonify({"username": username}), 200

    # Create new user account
    if request.method == "POST":
        if username:
            return jsonify({"error": "Must be logged off to create new account"}), 400

        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 415

        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Both username and password required"}), 400

        # Check if user already exists
        if svc.get_user(username):
            return jsonify({"error": "User already exists"}), 409

        svc.create_user(username, password)
        session["logged_in"] = True
        session["username"] = username
        return jsonify({
            "message": "User created successfully. Logged in under new username.",
            "username": username
        }), 201

    # Delete user account
    if request.method == "DELETE":
        if not username:
            return jsonify({"error": "Unauthorized"}), 401
        if not svc.get_user(username):
            return jsonify({"error": "User not found"}), 404

        svc.delete_user(username)
        session.clear()
        return jsonify({"message": "User deleted successfully. log in to a different account or create a new one."}), 200
    return None


@api_bp.route("/login", methods=["POST"])
def api_login():
    svc = get_session_service()

    if session.get("logged_in"):
        username = session.get("username")
        return jsonify({"error": f"{username} is already logged in"}), 400

    # Check Content-Type header
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    username = data.get("username").strip().lower()
    password = data.get("password").strip()

    if not username or not password:
        return jsonify({"error": "Both username and password required"}), 400

    if not svc.get_user(username):
        return jsonify({"error": "username not found"}), 404

    if svc.validate_user(username, password):
        session["logged_in"] = True
        session["username"] = username
        return jsonify({"message": f"{username} successfully logged in"}), 200
    return jsonify({"error": "Invalid password"}), 400


@api_bp.route("/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"message": "User successfully logged out"}), 200


# GENERIC PROFILE GET WITH PATHS #
def get_nested_value(data: dict, path: str):
    keys = path.split(".")
    current = data

    for key in keys:
        if not isinstance(current, dict):
            return None, f"'{key}' is not a dict level"
        if key not in current:
            return None, f"'{key}' not found"
        current = current[key]

    return current, None

@api_bp.route("/profile/<username>", methods=["GET"])
def api_get_from_profile(username):
    svc = get_session_service()

    path = request.args.get("path")  # e.g. "field2.subfield2-1"

    data = svc.get_profile(username)
    if not data:
        return jsonify({"error": "Profile not found"}), 404

    # No path → return whole document
    if not path:
        return jsonify(data), 200

    value, err = get_nested_value(data, path)
    if err:
        return jsonify({"error": err}), 404

    final_key = path.split(".")[-1]
    return jsonify({final_key: value}), 200


@api_bp.route("/profile/preset", methods=["POST", "PUT"])
def api_update_preset():
    svc = get_session_service()

    username = session.get("username")

    if not username:
        return jsonify({"error": "Unauthorized"}), 401

    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    task_name = data.get("task_name")
    if not task_name:
        return jsonify({"error": "task name required"}), 400

    task_time = data.get("task_time")
    if not task_time:
        return jsonify({"error": "task time required"}), 400

    preset_data = {
        "task_time": task_time,
    }

    svc.update_task_preset(username, task_name, preset_data)

    if request.method == "POST":
        return jsonify({
            "message": f"{task_name} task created successfully",
            f"{task_name}": preset_data,
        }), 201

    # if "PUT"
    return jsonify({
        "message": f"{task_name} task updated successfully",
        f"{task_name}": preset_data,
    }), 200


@api_bp.route("/profile/preset", methods=["GET"])
def api_get_preset():
    svc = get_session_service()

    username = session.get("username")

    if not username:
        return jsonify({"error": "Unauthorized"}), 401

    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    task_name = data.get("task_name")
    if not task_name:
        return jsonify({"error": "task name required"}), 400

    if task_name == "all":
        presets = svc.get_all_task_presets(username)

        if not presets:
            return jsonify({"error": "No presets configured."}), 404

        return jsonify({"presets": presets}), 200

    preset_data = svc.get_task_preset(username, task_name)

    if not preset_data:
        return jsonify({"error": "Preset not found"}), 404

    return jsonify({f"{task_name}": preset_data}), 200


@api_bp.route("/profile/preset", methods=["DELETE"])
def api_delete_preset():
    svc = get_session_service()

    username = session.get("username")

    if not username:
        return jsonify({"error": "Unauthorized"}), 401

    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    task_name = data.get("task_name")
    if not task_name:
        return jsonify({"error": "task name required"}), 400

    preset_data = svc.get_task_preset(username, task_name)

    if not preset_data:
        return jsonify({"error": "Preset not found"}), 404

    svc.delete_task_preset(username, task_name)

    return jsonify({"message": f"{task_name} task preset information successfully deleted."}), 200


@api_bp.route("/task/current", methods=["PUT"])
def api_set_task():
    svc = get_session_service()

    username = session.get("username")

    if not username:
        return jsonify({"error": "Unauthorized"}), 401

    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    task_name = data.get("task_name")
    if not task_name:
        return jsonify({"error": "task name required"}), 400

    preset_data = svc.get_task_preset(username, task_name)

    if not preset_data:
        return jsonify({"error": "Preset not found"}), 404

    svc.set_current_task(username, task_name)

    return jsonify({"message": f"{task_name} task has been set as the current task."}), 200


@api_bp.route("/task/current", methods=["GET"])
def api_get_task():
    svc = get_session_service()

    username = session.get("username")

    if not username:
        return jsonify({"error": "Unauthorized"}), 401

    current_task = svc.get_current_task(username)

    if not current_task:
        return jsonify({"error": "Current task not set"}), 400

    return jsonify({"message": f"The current task is the {current_task} task."}), 200


@api_bp.route("/session/latest", methods=["GET"])
def api_get_latest_session():
    svc = get_session_service()

    username = session.get("username")

    if not username:
        return jsonify({"error": "Unauthorized"}), 401

    latest_session = svc.get_session(username)
    task = latest_session.get("task")
    time = latest_session.get("elapsed_time")

    if not latest_session:
        return jsonify({"error": "No recorded session history."}), 400

    return jsonify({"task": task,
                    "time": time,
                    }), 200





