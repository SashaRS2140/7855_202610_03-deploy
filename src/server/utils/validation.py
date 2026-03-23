import re
from flask import jsonify, request


def require_json_content_type():
    """Ensure the request is JSON; returns an error response tuple if not."""
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415
    return None


def validate_login_data(data: dict[str, str]):
    errors = []
    allowed = {"email", "password", "confirm_password"}

    # Whitelist Check - reject unknown fields
    if unknown := set(data.keys()) - allowed:
        errors.append(f"Unknown fields: {unknown}")

    # Bounds Checking - enforce length limits
    if len(data.get("email", "")) > 50:
        errors.append("email must be 50 chars or less")

    # Pattern Validation - enforce format rules
    password = data.get("password", "")
    if not re.match(r"^[A-Za-z0-9]{7,50}$", password):
        errors.append("password invalid")

    return errors  # Return ALL errors


def validate_preset(data: dict):
    errors = []
    allowed = {"task_name", "task_time", "task_color"}

    # Whitelist Check - reject unknown fields
    if unknown := set(data.keys()) - allowed:
        errors.append(f"Unknown fields: {unknown}")

    # Bounds Checking for task_name
    if len(data.get("task_name", "")) > 30:
        errors.append("Task name must be 30 chars or less")

    # Type / Value Validation for task_time
    task_time = data.get("task_time", "")

    if task_time:
        if isinstance(task_time, int):
            if task_time <= 0:
                errors.append("Task time must be a positive integer")
            if task_time > 5940:
                errors.append("Task time must be less then 99 minutes")
        else:
            errors.append("Task time must be a positive integer")

    # Pattern Validation for task_color (RGB or RGBW)
    task_color = data.get("task_color", "")

    if task_color:
        if not isinstance(task_color, str) or not re.compile(r"^#[0-9a-fA-F]{6}([0-9a-fA-F]{2})?$").fullmatch(task_color):
            errors.append("Task color must be a valid hex RGB or RGBW string (e.g., '#0000ff' or '#0000ffff')")

    return errors  # Return ALL errors


def validate_user_info(data: dict):
    errors = []
    allowed = {"first_name", "last_name"}

    # Whitelist Check - reject unknown fields
    if unknown := set(data.keys()) - allowed:
        errors.append(f"Unknown fields: {unknown}")

    # Bounds Checking - enforce length limits
    if len(data.get("last_name", "")) > 50:
        errors.append("last name must be 50 chars or less")

    # Bounds Checking - enforce length limits
    if len(data.get("first_name", "")) > 50:
        errors.append("first must be 50 chars or less")

    return errors  # Return ALL errors


