import json
import time
from . import dashboard_bp
from src.server.decorators.auth import login_required
from src.server.utils.validation import require_json_content_type, validate_preset
from flask import render_template, redirect, url_for, current_app, Response, jsonify, request
from src.server.utils.repository import get_all_task_presets, get_task_preset, set_current_task, update_task_preset, get_current_task, get_session


@dashboard_bp.route("/")
@login_required
def home(uid: str):
    """Home page."""

    if uid:
        presets = get_all_task_presets(uid) or []
        tasks = []
        for index, preset in enumerate(presets, start=1):
            tasks.append({"id": index, "name": preset})
        return render_template("dashboard.html", tasks=tasks)

    return redirect(url_for("auth.login"))


@dashboard_bp.route("/task/timer")
@login_required
def stream_timer(uid: str):

    timer = current_app.timer

    def format_mmss(seconds):
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"

    def event_stream():
        while True:
            elapsed = timer.get_elapsed()
            target = timer.get_target()

            if elapsed < target:
                # countdown phase
                display_seconds = target - elapsed
                mode = "countdown"
            else:
                # overtime phase (count up past zero)
                display_seconds = elapsed - target
                mode = "overtime"

            payload = {
                "display_seconds": display_seconds,
                "display_mmss": format_mmss(display_seconds),
                "mode": mode,
                "elapsed": elapsed,
                "target": target
            }

            yield f"data: {json.dumps(payload)}\n\n"
            time.sleep(1)

    return Response(event_stream(), mimetype="text/event-stream")


#--- TEMP WEB API ---#

# replace with api_set_task & api_reset_timer #
@dashboard_bp.post("/task/current")
@login_required
def set_task(uid: str):
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

    task_time = preset_data.get("task_time")
    timer = current_app.timer
    timer.stop()
    timer.reset(task_time)

    return jsonify({"current_task": task_name}), 200


# replace with api_get_preset #
@dashboard_bp.get("/profile/preset/<task_name>")
@login_required
def get_preset(uid: str, task_name: str):
    """Get task preset data for dashboard UI via session auth."""
    task_name = task_name.strip().title()
    preset_data = get_task_preset(uid, task_name)
    if not preset_data:
        return jsonify({"error": "Preset not found"}), 404

    return jsonify({
        "task_name": task_name,
        "task_time": preset_data.get("task_time"),
        "task_color": preset_data.get("task_color"),
    }), 200


# replace with api_get_session_latest #
@dashboard_bp.get('/session/latest')
@login_required
def session_latest(uid: str):
    latest_session = get_session(uid)
    if not latest_session:
        return jsonify({"error": "No recorded session history."}), 400

    return jsonify({
        "task": latest_session.get("task"),
        "elapsed_time": latest_session.get("elapsed_time"),
        "timestamp": latest_session.get("timestamp"),
        "task_color": latest_session.get("task_color"),
    }), 200


# changed to api implementation #
@dashboard_bp.get('/sessions/calendar')
@login_required
def sessions_calendar(uid: str):
    """Return session data aggregated by day for calendar heatmap."""
    from datetime import datetime
    from src.server.utils.repository import get_sessions

    year = request.args.get("year", default=datetime.now().year, type=int)
    month = request.args.get("month", default=datetime.now().month, type=int)

    sessions = get_sessions(uid, limit=365)

    # Aggregate by date (filtered to requested month/year only)
    daily_totals = {}

    for session in sessions:
        ts = session.get("timestamp", "")[:10]  # YYYY-MM-DD
        try:
            session_year = int(ts[:4])
            session_month = int(ts[5:7])
            
            # Only include sessions from the requested month
            if session_year == year and session_month == month:
                if ts not in daily_totals:
                    daily_totals[ts] = {"count": 0, "total_time": 0}

                daily_totals[ts]["count"] += 1
                daily_totals[ts]["total_time"] += session.get("elapsed_time", 0)
        except (ValueError, IndexError):
            # Skip malformed timestamps
            continue

    return jsonify({
        "year": year,
        "month": month,
        "daily_data": daily_totals,
        "max_sessions": max([d["count"] for d in daily_totals.values()]) if daily_totals else 1
    }), 200


# replace with api_create_preset #
@dashboard_bp.post("/profile/preset")
@login_required
def create_preset(uid: str):
    """Create new preset task configuration from a JSON body."""

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
    update_task_preset(uid, task_name, preset_data)

    return jsonify({f"{task_name}": preset_data,}), 201


# replace with api_get_task #
@dashboard_bp.get("/task/current")
@login_required
def get_task(uid: str):
    """Get the current active task name."""

    current_task = get_current_task(uid)

    if not current_task:
        return jsonify({"error": "Current task not set"}), 400

    return jsonify({"current_task": current_task}), 200


# replace with api_update_preset #
@dashboard_bp.put("/profile/preset")
@login_required
def update_preset(uid: str):
    """Update preset task configuration from a JSON body."""

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
    preset_data = get_task_preset(uid, task_name)
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
    update_task_preset(uid, task_name, updated_preset_data)

    # Return updated task with all fields
    preset_data = get_task_preset(uid, task_name)
    return jsonify({f"{task_name}": preset_data,}), 200