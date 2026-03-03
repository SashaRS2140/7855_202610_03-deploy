import os
import requests
from flask import Blueprint, jsonify, request, current_app, session
from firebase_admin import auth
from src.server.services.session_services import validate_user_info, validate_preset, create_firebase_user, require_json_content_type, WEB_API_KEY, validate_profile, normalize_profile, validate_login_data
from functools import wraps

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


def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. Grab the expected key from the environment
        expected_key = os.environ.get("CUBE_API_KEY")

        # 2. Grab the provided key from the request headers
        key = request.headers.get("X-API-Key")

        # 3. Compare them
        if key != expected_key:
            return jsonify({"error": "Unauthorized"}), 401

        # 4. If they match, allow the route to execute normally
        return f(*args, **kwargs)
    return decorated_function


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

# This end-point is currently device only (no user auth required)
@api_bp.route("/task/control", methods=["POST"])
@require_api_key
def task_control():
    timer = get_timer_service()
    sess_svc = get_session_service()

    # Extract associated user account from CUBE UUID
    cube_uuid = request.headers.get("X-API-Key")
    uid = sess_svc.get_cube_user(cube_uuid)
    if not uid:
        return jsonify({"error": "Cube not registered with user account"}), 401

    # Check Content-Type header
    content_error = require_json_content_type()
    if content_error:
        return content_error

    # Extract data from JSON
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400


    action = data.get("action")
    elapsed_time = data.get("elapsed_seconds")

    # Load Current task information
    current_task = sess_svc.get_current_task(uid)
    if not current_task:
        return jsonify({"error": "Current task not set"}), 400

    task_data = sess_svc.get_task_preset(uid, current_task)
    task_time = task_data.get("task_time")
    tt_min = task_time // 60
    tt_sec = task_time % 60

    # Start action logic
    if action == "start":
        timer.start()
        return jsonify({"message": f"{current_task} task started"}), 200

    # Stop action logic
    if action == "stop":
        timer.stop()
        sess_svc.save_session(uid, current_task, elapsed_time)
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

    # Reset action logic
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

    # Format task name
    task_name = task_name.strip().title()

    # Return all presets if passed "all"
    if task_name == "All":
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
    task_name = data.get("task_name").strip().title()
    if not task_name:
        return jsonify({"error": "Task name required"}), 400

    # Check for existing preset
    preset_data = svc.get_task_preset(uid, task_name)
    if not preset_data:
        return jsonify({"error": "Task not found"}), 404

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


@api_bp.delete("/profile/preset")
def api_delete_preset():
    """Delete preset task configuration."""
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

    task_name = data.get("task_name").strip().title()
    if not task_name:
        return jsonify({"error": "task name required"}), 400

    preset_data = svc.get_task_preset(uid, task_name)

    if not preset_data:
        return jsonify({"error": "Preset not found"}), 404

    svc.delete_task_preset(uid, task_name)

    return jsonify({"message": f"{task_name} task preset information successfully deleted."}), 200


@api_bp.get("/task/current")
def api_get_task():
    """Get the current active task name."""
    svc = get_session_service()

    # Get current user uid
    (uid, error) = get_user_or_401()
    if error:
        return jsonify({"error": error}), 401

    current_task = svc.get_current_task(uid)

    if not current_task:
        return jsonify({"error": "Current task not set"}), 400

    return jsonify({"current_task": current_task}), 200


@api_bp.post("/task/current")
def api_set_task():
    """Set the current active task."""
    svc = get_session_service()

    # Get current user uid
    (uid, error) = get_user_or_401()
    if error:
        return jsonify({"error": error}), 401

    # Check for content error
    content_error = require_json_content_type()
    if content_error:
        return content_error

    # Parsing data from json
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    # Checking
    task_name = data.get("task_name").strip().title()
    if not task_name:
        return jsonify({"error": "task name required"}), 400

    preset_data = svc.get_task_preset(uid, task_name)

    if not preset_data:
        return jsonify({"error": "Preset not found"}), 404

    svc.set_current_task(uid, task_name)

    return jsonify({"current_task": task_name}), 200


@api_bp.get("/session/latest")
def api_get_latest_session():
    svc = get_session_service()

    # Get current user uid
    (uid, error) = get_user_or_401()
    if error:
        return jsonify({"error": error}), 401

    latest_session = svc.get_session(uid)
    task = latest_session.get("task")
    time = latest_session.get("elapsed_time")

    if not latest_session:
        return jsonify({"error": "No recorded session history."}), 400

    return jsonify({"task": task,
                    "time": time,
                    }), 200


@api_bp.post("/timer/reset")
def api_reset_timer():
    svc = get_session_service()
    timer = get_timer_service()

    # Get current user uid
    (uid, error) = get_user_or_401()
    if error:
        return jsonify({"error": error}), 401

    # checking for content error
    content_error = require_json_content_type()
    if content_error:
        return content_error

    # parsing data from json
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    # checking parsed data if valid
    task_name = data.get("task_name")
    if not task_name:
        return jsonify({"error": "task name required"}), 400

    # parsing preset data using task name
    preset_data = svc.get_task_preset(uid, task_name)

    # parsing current time from preset data
    task_time = preset_data.get("task_time")

    # resetting time from preset_data
    timer.reset(task_time)

    # return success
    return jsonify({"task_time": task_time}), 200


@api_bp.route("/profile/user_info/<field>", methods=["GET"])
def api_get_user_info(field):
    svc = get_session_service()

    # Get current user uid
    (uid, error) = get_user_or_401()
    if error:
        return jsonify({"error": error}), 401

    # Return all user data if passed "all"
    if field == "all":
        user_data = svc.get_all_user_info(uid)
        if not user_data:
            return jsonify({"error": "No information added."}), 404
        return jsonify({"user_info": user_data}), 200

    # Return user data
    user_data = svc.get_user_info(uid, field)
    if not user_data:
        return jsonify({"error": "No information added."}), 404

    return jsonify({f"{field}": user_data}), 200


@api_bp.put("/profile/user_info")
def api_update_user_info():
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
    error = validate_user_info(data)
    if error:
        return jsonify({"error": error}), 400

    # Prepare updated user info values (only include provided fields)
    first_name = data.get("first_name")
    last_name = data.get("last_name")

    user_info = {}
    if first_name is not None:
        user_info["first_name"] = first_name.strip().title() if first_name else ""
    if last_name is not None:
        user_info["last_name"] = last_name.strip().title() if last_name else ""

    # Save updated user info in database
    svc.save_user_info(uid, user_info)

    # Return updated user info with all fields
    updated_user_info = svc.get_all_user_info(uid)
    return jsonify({"user_info": updated_user_info}), 200


@api_bp.post("/profile/cube")
def api_save_cube():
    """Register a CUBE UUID with your user account."""
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

    cube_uuid = data.get("cube_uuid")
    if not cube_uuid:
        return jsonify({"error": "Cube uuid required"}), 400

    # Save cube uuid
    svc.save_cube_uuid(uid, cube_uuid)

    return jsonify({"cube_uuid": cube_uuid}), 200


#-----Below in Progress-----#


# MAYBE DON'T NEED #
@api_bp.route("/logout", methods=["POST"])
def api_logout():
    """Clear the session"""
    session.clear()
    return jsonify({"message": "User successfully logged out"}), 200
