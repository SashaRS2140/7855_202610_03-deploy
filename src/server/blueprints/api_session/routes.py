from . import api_session_bp
from datetime import datetime
from flask import request, jsonify
from src.server.decorators.auth import require_jwt
from src.server.logging_config import get_logger
from src.server.utils.api_response import api_error
from src.server.utils.validation import require_json_content_type
from src.server.utils.repository import get_session, set_current_task, get_current_task, get_task_preset, get_sessions, get_sessions_by_date_range

logger = get_logger(__name__)


##########################################################################
###                       SESSION API ROUTES                           ###
##########################################################################


@api_session_bp.get("/task/current")
@require_jwt
def api_get_task(uid: str):
    """Get the current active task name."""

    current_task = get_current_task(uid)

    if not current_task:
        return api_error(
            "Current task not set",
            status=400,
            error_type="no_current_task"
        )
    
    logger.info(f"Retrieved current task: {current_task}", extra={
        'user_id': uid,
        'endpoint': '/api/task/current',
        'method': 'GET',
        'task_name': current_task
    })

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
        return api_error(
            "Invalid JSON",
            status=400,
            error_type="invalid_json"
        )

    # Checking
    task_name = data.get("task_name").strip().title()
    if not task_name:
        return api_error(
            "task name required",
            status=400,
            error_type="missing_task_name"
        )

    preset_data = get_task_preset(uid, task_name)

    if not preset_data:
        return api_error(
            "Preset not found",
            status=404,
            error_type="preset_not_found",
            extra={
                'task_name': task_name
            }
        )

    set_current_task(uid, task_name)
    
    logger.info(f"Current task set: {task_name}", extra={
        'user_id': uid,
        'endpoint': '/api/task/current',
        'method': 'POST',
        'task_name': task_name
    })

    return jsonify({"current_task": task_name}), 200


@api_session_bp.get("/sessions/latest")
@require_jwt
def api_get_latest_session(uid: str):
    """Get the latest session data form the session history database."""

    latest_session = get_session(uid)
    if not latest_session:
        return api_error(
            "No recorded session history.",
            status=400,
            error_type="no_session_history"
        )

    task = latest_session.get("task")
    elapsed_time = latest_session.get("elapsed_time")
    timestamp = latest_session.get("timestamp")
    task_color = latest_session.get("task_color")
    
    logger.info(f"Retrieved latest session: {task}", extra={
        'user_id': uid,
        'endpoint': '/api/session/latest',
        'method': 'GET',
        'task_name': task,
        'elapsed_seconds': elapsed_time
    })

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

    limit = request.args.get("limit", default=100, type=int)
    offset = request.args.get("offset", default=0, type=int)

    all_sessions = get_sessions(uid, limit=limit + offset)
    paginated = all_sessions[offset:offset+limit]
    
    logger.info(f"Retrieved sessions", extra={
        'user_id': uid,
        'endpoint': '/api/sessions',
        'method': 'GET',
        'limit': limit,
        'offset': offset,
        'total_count': len(all_sessions),
        'returned_count': len(paginated)
    })

    return jsonify({
        "sessions": paginated,
        "total": len(all_sessions)
    }), 200


@api_session_bp.get("/sessions/range")
@require_jwt
def api_get_sessions_range(uid: str):
    """Get sessions within a date range."""

    start = request.args.get("start")  # YYYY-MM-DD
    end = request.args.get("end")

    if not start or not end:
        return api_error(
            "start and end dates required (YYYY-MM-DD)",
            status=400,
            error_type="missing_params"
        )

    sessions = get_sessions_by_date_range(uid, start, end)
    
    logger.info(f"Retrieved sessions by date range", extra={
        'user_id': uid,
        'endpoint': '/api/sessions/range',
        'method': 'GET',
        'start_date': start,
        'end_date': end,
        'session_count': len(sessions)
    })

    return jsonify({"sessions": sessions}), 200


@api_session_bp.get('/sessions/calendar')
@require_jwt
def api_get_sessions_calendar(uid: str):
    """Get session data aggregated by day for calendar heatmap."""

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

    logger.info(f"Retrieved calendar data", extra={
        'user_id': uid,
        'endpoint': '/api/sessions/calendar',
        'method': 'GET',
        'year': year,
        'month': month,
        'days_with_sessions': len(daily_totals)
    })

    return jsonify({
        "year": year,
        "month": month,
        "daily_data": daily_totals,
        "max_sessions": max([d["count"] for d in daily_totals.values()]) if daily_totals else 1
    }), 200