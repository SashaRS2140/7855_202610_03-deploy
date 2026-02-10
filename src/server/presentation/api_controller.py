from flask import Blueprint, jsonify, request, current_app, session
from bcrypt import hashpw, checkpw, gensalt

api_bp = Blueprint('api', __name__)


def get_session_service():
    """Helper to access the service layer."""
    return current_app.session_service


def get_hw_service():
    return current_app.hw_service


##########################################################################
###                             CUBE API                               ###
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


##########################################################################
###                             JSON API                               ###
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
            "profile": profile_data.get("profile")
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
        return jsonify({
            "message": "User successfully logged in",
            "username": username
        }), 200
    return jsonify({"error": "Invalid password"}), 400


@api_bp.route("/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"message": "User successfully logged out"}), 200
