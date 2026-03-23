import re
from . import api_bp
from flask import request, jsonify, current_app
from src.server.decorators.auth import require_jwt, require_api_key
from src.server.utils.validation import require_json_content_type, validate_preset, validate_user_info
from src.server.utils.repository import save_user_info, save_cube_uuid, get_user_info, get_all_user_info, get_session, set_current_task, delete_task_preset, update_task_preset, get_all_task_presets, get_profile, get_cube_user, get_current_task, save_session, get_task_preset


def normalize_task_color(task_color):
    if not task_color or not isinstance(task_color, str):
        return task_color

    task_color = task_color.strip().lower()

    if re.fullmatch(r"^#[0-9a-f]{6}$", task_color):
        return task_color + "ff"

    if re.fullmatch(r"^#[0-9a-f]{8}$", task_color):
        return task_color

    # fallback as provided
    return task_color


##########################################################################
###                         CUBE API ROUTES                            ###
##########################################################################


# This end-point is currently device only (no user auth required)
@api_bp.post("/task/control")
@require_api_key
def task_control(cube_uuid: str):

    # Get timer object
    timer = current_app.timer

    # Extract associated user account from CUBE UUID
    uid = get_cube_user(cube_uuid)
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
    current_task = get_current_task(uid)
    if not current_task:
        return jsonify({"error": "Current task not set"}), 400

    task_data = get_task_preset(uid, current_task)
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
        task_color = task_data.get("task_color")
        save_session(uid, current_task, elapsed_time, task_color)
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
###                       Profile API ROUTES                           ###
##########################################################################


@api_bp.get("/profile")
@require_jwt
def api_get_profile(uid: str):
    """Return all the current user's profile data."""

    # Get all profile data
    profile_data = get_profile(uid)

    return jsonify({"profile": profile_data}), 200


@api_bp.route("/profile/user_info/<field>", methods=["GET"])
@require_jwt
def api_get_user_info(uid: str, field: str):

    # Return all user data if passed "all"
    if field == "all":
        user_data = get_all_user_info(uid)
        if not user_data:
            return jsonify({"error": "No information added."}), 404
        return jsonify({"user_info": user_data}), 200

    # Return user data
    user_data = get_user_info(uid, field)
    if not user_data:
        return jsonify({"error": "No information added."}), 404

    return jsonify({f"{field}": user_data}), 200


@api_bp.put("/profile/user_info")
@require_jwt
def api_update_user_info(uid: str):

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
    save_user_info(uid, user_info)

    # Return updated user info with all fields
    updated_user_info = get_all_user_info(uid)
    return jsonify({"user_info": updated_user_info}), 200


@api_bp.post("/profile/cube")
@require_jwt
def api_save_cube(uid: str):
    """Register a CUBE UUID with your user account."""

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
    save_cube_uuid(uid, cube_uuid)

    return jsonify({"cube_uuid": cube_uuid}), 200


##########################################################################
###                       PRESETS API ROUTES                           ###
##########################################################################

# helper function
def extract_preset_data():
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

    return data


@api_bp.route("/profile/preset/<task_name>", methods=["GET"])
@require_jwt
def api_get_preset(uid: str, task_name: str):
    """Get preset task configurations."""

    # Format task name
    task_name = task_name.strip().title()

    # Return all presets if passed "All"
    if task_name == "All":
        presets = get_all_task_presets(uid)
        if not presets:
            return jsonify({"error": "No presets configured."}), 404
        return jsonify({"presets": presets}), 200

    # Return preset data
    preset_data = get_task_preset(uid, task_name)
    if not preset_data:
        return jsonify({"error": "Preset not found"}), 404
    return jsonify({f"{task_name}": preset_data}), 200


@api_bp.post("/profile/preset")
@require_jwt
def api_create_preset(uid: str):
    """Create new preset task configuration from a JSON body."""

    # Extract preset data from JSON
    data = extract_preset_data()

    # Organize preset task data
    task_name = data.get("task_name").strip().title()
    if not task_name:
        return jsonify({"error": "task name required"}), 400

    task_time = data.get("task_time")
    if not task_time:
        return jsonify({"error": "task time required"}), 400

    task_color = normalize_task_color(data.get("task_color"))
    if not task_color:
        return jsonify({"error": "task color required"}), 400

    preset_data = {
        "task_time": task_time,
        "task_color": task_color,
    }

    # Save new preset task in database
    update_task_preset(uid, task_name, preset_data)

    return jsonify({f"{task_name}": preset_data,}), 201


@api_bp.put("/profile/preset")
@require_jwt
def api_update_preset(uid: str):
    """Update preset task configuration from a JSON body."""

    #Extract preset data from JSON
    data = extract_preset_data()

    # Prepare updated preset task data (only include provided fields)
    task_name = data.get("task_name").strip().title()
    if not task_name:
        return jsonify({"error": "Task name required"}), 400

    # Check for existing preset
    preset_data = get_task_preset(uid, task_name)
    if not preset_data:
        return jsonify({"error": "Task not found"}), 404

    task_time = data.get("task_time")
    task_color = data.get("task_color")

    updated_preset_data = {}
    if task_time is not None:
        updated_preset_data["task_time"] = task_time if task_time else ""
    if task_color is not None:
        updated_preset_data["task_color"] = normalize_task_color(task_color) if task_color else ""

    # Save updated preset task in database
    update_task_preset(uid, task_name, updated_preset_data)

    # Return updated task with all fields
    preset_data = get_task_preset(uid, task_name)
    return jsonify({f"{task_name}": preset_data,}), 200


@api_bp.delete("/profile/preset")
@require_jwt
def api_delete_preset(uid: str):
    """Delete preset task configuration."""

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

    preset_data = get_task_preset(uid, task_name)

    if not preset_data:
        return jsonify({"error": "Preset not found"}), 404

    delete_task_preset(uid, task_name)

    return jsonify({"message": f"{task_name} task preset information successfully deleted."}), 200


##########################################################################
###                       SESSION API ROUTES                           ###
##########################################################################


@api_bp.get("/task/current")
@require_jwt
def api_get_task(uid: str):
    """Get the current active task name."""

    current_task = get_current_task(uid)

    if not current_task:
        return jsonify({"error": "Current task not set"}), 400

    return jsonify({"current_task": current_task}), 200


@api_bp.post("/task/current")
@require_jwt
def api_set_task(uid: str):
    """Set the current active task."""

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

    preset_data = get_task_preset(uid, task_name)

    if not preset_data:
        return jsonify({"error": "Preset not found"}), 404

    set_current_task(uid, task_name)

    return jsonify({"current_task": task_name}), 200


@api_bp.get("/session/latest")
@require_jwt
def api_get_latest_session(uid: str):

    latest_session = get_session(uid)
    if not latest_session:
        return jsonify({"error": "No recorded session history."}), 400

    task = latest_session.get("task")
    elapsed_time = latest_session.get("elapsed_time")
    timestamp = latest_session.get("timestamp")
    task_color = latest_session.get("task_color")

    return jsonify({
        "task": task,
        "elapsed_time": elapsed_time,
        "timestamp": timestamp,
        "task_color": task_color,
    }), 200


##########################################################################
###                        TIMER API ROUTES                            ###
##########################################################################


#-- MAY NOT NEED --#
@api_bp.post("/timer/reset")
@require_jwt
def api_reset_timer(uid: str):

    # Get timer object
    timer = current_app.timer

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
    preset_data = get_task_preset(uid, task_name)

    # parsing current time from preset data
    task_time = preset_data.get("task_time")

    # resetting time from preset_data
    timer.reset(task_time)

    # return success
    return jsonify({"task_time": task_time}), 200