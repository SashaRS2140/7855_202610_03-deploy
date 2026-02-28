import requests
from flask import Blueprint, jsonify, request, current_app, session
from firebase_admin import auth
from server.services.session_services import validate_preset, create_firebase_user, require_json_content_type, WEB_API_KEY, validate_profile, normalize_profile, validate_login_data


api_bp = Blueprint('api', __name__)


##########################################################################
###                        HELPER FUNCTIONS                            ###
##########################################################################


def get_session_service():
    """Helper to access the service layer."""
    return current_app.session_service


def get_hw_service():
    return current_app.hw_service


def get_timer_service():
    return current_app.timer


def get_user_or_401():
    """Return the current API user or an Unauthorized response."""
    header = request.headers.get("Authorization")
    if not header or not header.startswith("Bearer "):
        return None, "Invalid token format"
    token = header.split(" ")[1]

    try:
        # Validates cryptographic signature
        decoded_token = auth.verify_id_token(token)
        return decoded_token["uid"], None
    except Exception as e:
        return None, f"Unauthorized: {str(e)}"


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

    content_error = require_json_content_type()
    if content_error:
        return content_error

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


@api_bp.route("/login", methods=["POST"])
def api_login():
    """Login via Firestore Authentication. Return JWT."""
    # Check Content-Type header
    content_error = require_json_content_type()
    if content_error:
        return content_error

    # Extract data from JSON
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    # Send login credentials to Firestore Authentication Service for verification
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={WEB_API_KEY}"
    payload = {"email": data["email"], "password": data["password"], "returnSecureToken": True}
    res = requests.post(url, json=payload)
    if res.status_code == 200:
        # Return JWT on success
        return jsonify({"token": res.json()["idToken"]}), 200

    return jsonify({"error": "Invalid credentials"}), 401


@api_bp.route("/signup", methods=["POST"])
def api_signup():
    """Create new user account. Return new account UID."""
    svc = get_session_service()

    # Check Content-Type header
    content_error = require_json_content_type()
    if content_error:
        return content_error

    # Extract data from JSON
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    # Validate input data
    error = validate_login_data(data)
    if error:
        return jsonify({"error": error}), 400

    # Extract input data
    email = data["email"]
    password = data["password"]

    # Create user via Firebase Authentication Service
    (user, error) = create_firebase_user(email, password)
    if error:
        return jsonify({"error": error}), 400

    # Save new user information to database
    uid = user.uid
    user_info = {"email": email, "role": "user"}
    svc.save_user_info(uid, user_info)

    return jsonify({"uid": uid}), 201


@api_bp.get("/profile")
def api_get_profile():
    """Return all the current user's profile data."""
    svc = get_session_service()

    # Get current user uid
    (uid, error) = get_user_or_401()
    if error:
        return jsonify({"error": error}), 401

    # Get all profile data
    profile_data = svc.get_profile(uid)

    return jsonify({"profile": profile_data}), 200


@api_bp.route("/profile/preset/<task_name>", methods=["GET"])
def api_get_preset(task_name):
    """Get preset task configurations."""
    svc = get_session_service()

    # Get current user uid
    (uid, error) = get_user_or_401()
    if error:
        return jsonify({"error": error}), 401

    # Check Content-Type header
    content_error = require_json_content_type()
    if content_error:
        return content_error

    # Extract data from JSON
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    # Return all presets if passed "all"
    if task_name == "all":
        presets = svc.get_all_task_presets(uid)
        if not presets:
            return jsonify({"error": "No presets configured."}), 404
        return jsonify({"presets": presets}), 200

    # Return preset data
    preset_data = svc.get_task_preset(uid, task_name)
    if not preset_data:
        return jsonify({"error": "Preset not found"}), 404
    return jsonify({f"{task_name}": preset_data}), 200


@api_bp.post("/profile/preset")
def api_create_preset():
    """Create new preset task configuration from a JSON body."""
    svc = get_session_service()

    # Get current user uid
    (uid, error) = get_user_or_401()
    if error:
        return jsonify({"error": error}), 401

    # Check Content-Type header
    content_error = require_json_content_type()
    if content_error:
        return content_error

    # Extract data from JSON
    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    # Validate input data
    error = validate_preset(data)
    if error:
        return jsonify({"error": error}), 400

    # Organize preset task data
    task_name = data.get("task_name").strip().title()
    if not task_name:
        return jsonify({"error": "task name required"}), 400

    task_time = data.get("task_time")
    if not task_time:
        return jsonify({"error": "task time required"}), 400

    task_color = data.get("task_color").lower()
    if not task_color:
        return jsonify({"error": "task color required"}), 400

    preset_data = {
        "task_time": task_time,
        "task_color": task_color,
    }

    # Save new preset task in database
    svc.update_task_preset(uid, task_name, preset_data)

    return jsonify({f"{task_name}": preset_data,}), 201


@api_bp.put("/profile/preset")
def api_update_preset():
    """Update preset task configuration from a JSON body."""
    svc = get_session_service()

    # Get current user uid
    (uid, error) = get_user_or_401()
    if error:
        return jsonify({"error": error}), 401

    # Check Content-Type header
    content_error = require_json_content_type()
    if content_error:
        return content_error

    # Extract data from JSON
    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    # Validate input data
    error = validate_preset(data)
    if error:
        return jsonify({"error": error}), 400

    # Prepare updated preset task data (only include provided fields)
    task_name = data.get("task_name")
    if not task_name:
        return jsonify({"error": "task name required"}), 400

    task_time = data.get("task_time")
    task_color = data.get("task_color")

    updated_preset_data = {}
    if task_time is not None:
        updated_preset_data["task_time"] = task_time if task_time else ""
    if task_color is not None:
        updated_preset_data["task_color"] = task_color.lower() if task_color else ""

    # Save updated preset task in database
    svc.update_task_preset(uid, task_name, updated_preset_data)

    # Return updated task with all fields
    preset_data = svc.get_task_preset(uid, task_name)
    return jsonify({f"{task_name}": preset_data,}), 200


#-----Below in Progress-----#


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
        content_error = require_json_content_type()
        if content_error:
            return content_error

        # Parse JSON payload
        try:
            data = request.get_json()
        except Exception:
            return jsonify({"error": "Invalid JSON"}), 400

        # Validate the data
        error = validate_profile(data)
        if error:
            return jsonify({"error": error}), 400

        # Valid -> normalize and save
        normalized_profile = normalize_profile(data)
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


# MAYBE DON'T NEED #
@api_bp.route("/logout", methods=["POST"])
def api_logout():
    """Clear the session"""
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








@api_bp.route("/profile/preset", methods=["DELETE"])
def api_delete_preset():
    svc = get_session_service()

    username = session.get("username")

    if not username:
        return jsonify({"error": "Unauthorized"}), 401

    content_error = require_json_content_type()
    if content_error:
        return content_error

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


@api_bp.route("/task/current", methods=["PUT", "POST"])
def api_set_task():
    svc = get_session_service()

    username = session.get("username")

    if not username:
        return jsonify({"error": "Unauthorized"}), 401

    content_error = require_json_content_type()
    if content_error:
        return content_error

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

    return jsonify({"current_task": task_name}), 200


@api_bp.route("/task/current", methods=["GET"])
def api_get_task():
    svc = get_session_service()

    username = session.get("username")

    if not username:
        return jsonify({"error": "Unauthorized"}), 401

    current_task = svc.get_current_task(username)

    if not current_task:
        return jsonify({"error": "Current task not set"}), 400

    return jsonify({"current_task": current_task}), 200


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





