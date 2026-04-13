from . import api_cube_bp
from flask import request, jsonify, current_app
from src.server.decorators.auth import require_api_key
from src.server.logging_config import get_logger
from src.server.utils.validation import require_json_content_type, parse_time
from src.server.utils.repository import get_cube_user, get_current_task, save_session, get_task_preset

logger = get_logger(__name__)


##########################################################################
###                         CUBE API ROUTES                            ###
##########################################################################


@api_cube_bp.post("/task/control")
@require_api_key
def api_task_control(cube_uuid: str):

    print("Received task control request from cube:", cube_uuid)
    """Interface between hardware cube, Firestore database, and timer service."""

    # Get timer object
    timer = current_app.timer

    # Extract associated user account from CUBE UUID
    uid = get_cube_user(cube_uuid)
    if not uid:
        logger.warning(f"Task control attempted with unregistered cube '{cube_uuid}'", extra={
            'endpoint': '/api/task/control',
            'method': 'POST',
            'error_type': 'unregistered_cube'
        })
        return jsonify({"error": "Cube not registered with user account"}), 401

    # Check Content-Type header
    content_error = require_json_content_type()
    if content_error:
        return content_error

    # Extract data from JSON
    data = request.get_json()
    print("\n data: ", data)
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
    tt_min, tt_sec = parse_time(task_time)

    task_color = task_data.get("task_color")

    # Start action logic
    if action == "start":
        timer.start()
        logger.info(f"Task '{current_task}' started via cube", extra={
            'user_id': uid,
            'endpoint': '/api/task/control',
            'method': 'POST',
            'action': 'start'
        })
        return jsonify({"message": f"{current_task} task started"}), 200

    # Stop action logic
    if action == "stop":
        timer.stop()
        save_session(uid, current_task, elapsed_time)
        logger.info(f"Task '{current_task}' stopped, {elapsed_time}s elapsed", extra={
            'user_id': uid,
            'endpoint': '/api/task/control',
            'method': 'POST',
            'action': 'stop',
            'elapsed_seconds': elapsed_time
        })
        if elapsed_time <= task_time:
            min, sec = parse_time(elapsed_time)
            if not min and not sec:
                return jsonify({"error": "Elapsed time must be a positive non-zero integer."}), 400
            return jsonify({"message": f"{current_task} task stopped. "
                                       f"{min}m:{sec}s of session time logged."
                            }), 200
        else:
            extra_time = elapsed_time - task_time
            min, sec = parse_time(extra_time)
            return jsonify({"message": f"{current_task} task stopped. "
                                       f"{tt_min}m:{tt_sec}s of session time + "
                                       f"{min}m:{sec}s of extra session time logged."
                            }), 200

    # Reset action logic
    if action == "reset":
        timer.reset(task_time)
        logger.info(f"Task '{current_task}' reset via cube", extra={
            'user_id': uid,
            'endpoint': '/api/task/control',
            'method': 'POST',
            'action': 'reset',
            'task_time': task_time
        })
        return jsonify({"message": f"{current_task} task reset",
                        "task_name": current_task,
                        "task_time": task_time,
                        "task_color": task_color
                        }), 200