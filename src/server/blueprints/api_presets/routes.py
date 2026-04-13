from . import api_presets_bp
from flask import request, jsonify
from src.server.decorators.auth import require_jwt
from src.server.logging_config import get_logger
from src.server.utils.api_response import api_error
from src.server.utils.validation import normalize_task_color, require_json_content_type, validate_preset
from src.server.utils.repository import delete_task_preset, update_task_preset, get_all_task_presets, get_task_preset

logger = get_logger(__name__)


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
        return api_error(
            "Invalid JSON",
            status=400,
            error_type="invalid_json"
        )

    # Validate input data
    error = validate_preset(data)
    if error:
        return api_error(
            error,
            status=400,
            error_type="validation_failed"
        )

    return data


@api_presets_bp.route("/profile/preset/<task_name>", methods=["GET"])
@require_jwt
def api_get_preset(uid: str, task_name: str):
    """Get preset task configurations."""

    # Format task name
    task_name = task_name.strip().title()

    # Return all presets if passed "All"
    if task_name == "All":
        presets = get_all_task_presets(uid)
        if not presets:
            return api_error(
                "No presets configured.",
                status=404,
                error_type="no_presets"
            )
        logger.info(f"Retrieved all presets for user", extra={
            'user_id': uid,
            'endpoint': '/api/profile/preset/All',
            'method': 'GET',
            'preset_count': len(presets)
        })
        return jsonify({"presets": presets}), 200

    # Return preset data
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
    logger.info(f"Retrieved preset: {task_name}", extra={
        'user_id': uid,
        'endpoint': '/api/profile/preset/{task_name}',
        'method': 'GET',
        'task_name': task_name
    })
    return jsonify({f"{task_name}": preset_data}), 200


@api_presets_bp.post("/profile/preset")
@require_jwt
def api_create_preset(uid: str):
    """Create new preset task configuration."""

    # Extract preset data from JSON
    data = extract_preset_data()

    # Organize preset task data
    task_name = (data.get("task_name") or "").strip().title()
    if not task_name:
        return api_error(
            "task name required",
            status=400,
            error_type="missing_task_name"
        )

    task_time = data.get("task_time")
    if not task_time:
        return api_error(
            "task time required",
            status=400,
            error_type="missing_task_time"
        )

    task_color = normalize_task_color(data.get("task_color"))
    if not task_color:
        return api_error(
            "task color required",
            status=400,
            error_type="missing_task_color"
        )

    preset_data = {
        "task_time": task_time,
        "task_color": task_color,
    }

    # Save new preset task in database
    update_task_preset(uid, task_name, preset_data)
    
    logger.info(f"Preset created: {task_name}", extra={
        'user_id': uid,
        'endpoint': '/api/profile/preset',
        'method': 'POST',
        'task_name': task_name,
        'task_time': task_time
    })

    return jsonify({f"{task_name}": preset_data,}), 201


@api_presets_bp.put("/profile/preset")
@require_jwt
def api_update_preset(uid: str):
    """Update preset task configuration."""

    #Extract preset data from JSON
    data = extract_preset_data()

    # Prepare updated preset task data (only include provided fields)
    task_name = (data.get("task_name") or "").strip().title()
    if not task_name:
        return api_error(
            "Task name required",
            status=400,
            error_type="missing_task_name"
        )

    # Check for existing preset
    preset_data = get_task_preset(uid, task_name)
    if not preset_data:
        return api_error(
            "Task not found",
            status=404,
            error_type="preset_not_found",
            extra={
                'task_name': task_name
            }
        )

    task_time = data.get("task_time")
    task_color = data.get("task_color")

    updated_preset_data = {}
    if task_time is not None:
        updated_preset_data["task_time"] = task_time if task_time else ""
    if task_color is not None:
        updated_preset_data["task_color"] = normalize_task_color(task_color) if task_color else ""

    # Save updated preset task in database
    update_task_preset(uid, task_name, updated_preset_data)
    
    logger.info(f"Preset updated: {task_name}", extra={
        'user_id': uid,
        'endpoint': '/api/profile/preset',
        'method': 'PUT',
        'task_name': task_name
    })

    # Return updated task with all fields
    preset_data = get_task_preset(uid, task_name)
    return jsonify({f"{task_name}": preset_data,}), 200


@api_presets_bp.delete("/profile/preset")
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
        return api_error(
            "Invalid JSON",
            status=400,
            error_type="invalid_json"
        )

    task_name = (data.get("task_name") or "").strip().title()
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

    delete_task_preset(uid, task_name)
    
    logger.info(f"Preset deleted: {task_name}", extra={
        'user_id': uid,
        'endpoint': '/api/profile/preset',
        'method': 'DELETE',
        'task_name': task_name
    })

    return jsonify({"message": f"{task_name} task preset information successfully deleted."}), 200