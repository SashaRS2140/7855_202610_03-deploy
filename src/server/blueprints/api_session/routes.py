from . import api_session_bp
from flask import request, jsonify
from src.server.decorators.auth import require_jwt
from src.server.utils.validation import require_json_content_type
from src.server.utils.repository import get_session, set_current_task, get_current_task, get_task_preset


##########################################################################
###                       SESSION API ROUTES                           ###
##########################################################################


@api_session_bp.get("/task/current")
@require_jwt
def api_get_task(uid: str):
    """Get the current active task name."""

    current_task = get_current_task(uid)

    if not current_task:
        return jsonify({"error": "Current task not set"}), 400

    return jsonify({"current_task": current_task}), 200


@api_session_bp.post("/task/current")
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


@api_session_bp.get("/session/latest")
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


@api_session_bp.get("/sessions")
@require_jwt
def api_get_sessions(uid: str):
    """Get paginated session list for a user."""
    from src.server.utils.repository import get_sessions

    limit = request.args.get("limit", default=100, type=int)
    offset = request.args.get("offset", default=0, type=int)

    all_sessions = get_sessions(uid, limit=limit + offset)
    paginated = all_sessions[offset:offset+limit]

    return jsonify({
        "sessions": paginated,
        "total": len(all_sessions)
    }), 200


@api_session_bp.get("/sessions/range")
@require_jwt
def api_get_sessions_range(uid: str):
    """Get sessions within a date range."""
    from src.server.utils.repository import get_sessions_by_date_range

    start = request.args.get("start")  # YYYY-MM-DD
    end = request.args.get("end")

    if not start or not end:
        return jsonify({"error": "start and end dates required (YYYY-MM-DD)"}), 400

    sessions = get_sessions_by_date_range(uid, start, end)

    return jsonify({"sessions": sessions}), 200