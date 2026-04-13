import requests
import re
import time
from . import auth_bp
from config import Config
from src.server.decorators.auth import login_required
from src.server.utils.repository import save_user_info
from src.server.utils.auth import create_firebase_user
from src.server.logging_config import get_logger
from src.server.utils.api_response import api_error
from flask import request, render_template, redirect, url_for, session, jsonify, has_request_context
from src.server.utils.validation import validate_login_data, require_json_content_type

logger = get_logger(__name__)


def _sanitize_invalid_json_body(raw_text: str, max_length: int = 200) -> str:
    preview = raw_text.strip().replace("\n", " ").replace("\r", " ")
    preview = re.sub(r'(?i)"password"\s*:\s*"[^"]*"', '"password":"[REDACTED]"', preview)
    return preview[:max_length]


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Login page."""

    if request.method == "GET":
        return render_template("login.html")

    # Handle JSON API login
    if request.is_json:
        return api_login()

    # Handle web form login
    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        logger.warning("Login attempt missing credentials", extra={
            'endpoint': '/login',
            'method': 'POST',
            'error_type': 'missing_credentials',
            'user_email': email if email else None
        })
        return render_template("login.html", error="Email and password are required")

    # Use Firebase Identity REST API to authenticate
    try:
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={Config.WEB_API_KEY}"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }

        res = requests.post(url, json=payload, timeout=10)

        if res.status_code == 200:
            token_data = res.json()
            # For web sessions, we'll use the uid from the response
            uid = token_data.get("localId")
            session["logged_in"] = True
            session["uid"] = uid
            session["email"] = email
            session["jwt_token"] = token_data.get("idToken")
            logger.info(f"User '{email}' logged in successfully", extra={
                'user_id': uid,
                'endpoint': '/login',
                'method': 'POST'
            })
            return redirect(url_for("dashboard.home"))

        error_data = res.json().get("error", {})
        error_message = error_data.get("message", "Invalid credentials")
        if "INVALID_LOGIN_CREDENTIALS" in error_message:
            error_message = "Invalid email or password"
        logger.warning(f"Failed login attempt for email '{email}'", extra={
            'endpoint': '/login',
            'method': 'POST',
            'error_type': 'invalid_credentials'
        })
        return render_template("login.html", error=error_message)
    except requests.RequestException as e:
        logger.error(f"Authentication service error: {str(e)}", extra={
            'endpoint': '/login',
            'method': 'POST',
            'error_type': 'service_unavailable'
        })
        return render_template("login.html", error="Authentication service unavailable")


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    """Sign up page. Create a new user account."""

    if request.method == "GET":
        return render_template("signup.html")

    # Handle form submission (web)
    if request.content_type and "application/json" in request.content_type:
        return api_signup()

    # Validate input data
    data = request.form.to_dict()
    email = data.get("email")
    error = validate_login_data(data)
    if error:
        logger.warning("Signup validation failed", extra={
            'endpoint': '/signup',
            'method': 'POST',
            'error_type': 'validation_failed',
            'user_email': email
        })
        return render_template("signup.html", error=error)

    # Extract input data
    email = data["email"]
    password = data["password"]
    confirm_password = data["confirm_password"]

    # Validate passwords match
    if password != confirm_password:
        return render_template("signup.html", error="Passwords do not match")

    # Create user via Firebase Authentication Service
    (user, error) = create_firebase_user(email, password)
    if error:
        logger.warning(f"Failed signup attempt for email '{email}'", extra={
            'endpoint': '/signup',
            'method': 'POST',
            'error_type': 'user_creation_failed'
        })
        return render_template("signup.html", error=error)

    # Save new user information to database
    uid = user.uid
    user_info = {"email": email, "role": "user"}
    save_user_info(uid, user_info)
    
    logger.info(f"New user '{email}' registered successfully", extra={
        'user_id': uid,
        'endpoint': '/signup',
        'method': 'POST'
    })

    return redirect(url_for("auth.login"))


@auth_bp.route("/logout")
@login_required
def logout(uid: str):
    """Clear the session and return to login page."""

    session.clear()
    return redirect(url_for("auth.login"))


def api_login():
    """JSON API endpoint for login. Returns a JWT token."""

    # Check Content-Type header
    content_error = require_json_content_type()
    if content_error:
        return content_error

    # Extract data from JSON
    data = request.get_json()
    if not data:
        invalid_body = request.get_data(as_text=True)
        return api_error(
            "Invalid JSON",
            status=400,
            error_type="invalid_json",
            extra={
                'content_type': request.content_type,
                'body_length': len(invalid_body),
                'body_preview': _sanitize_invalid_json_body(invalid_body)
            }
        )

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return api_error(
            "Email and password are required",
            status=400,
            error_type="missing_credentials",
            extra={
                'user_email': email if email else None
            }
        )

    # Send login credentials to Firestore Authentication Service for verification
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={Config.WEB_API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    try:
        res = requests.post(url, json=payload, timeout=10)

        if res.status_code == 200:
            # Return JWT on success
            uid = res.json().get("localId")
            logger.info(f"API login successful for '{email}'", extra={
                'user_id': uid,
                'endpoint': '/api/login',
                'method': 'POST'
            })
            return jsonify({"token": res.json()["idToken"]}), 200

        return api_error(
            "Invalid credentials",
            status=401,
            error_type="invalid_credentials"
        )
    except requests.RequestException as e:
        return api_error(
            "Authentication service unavailable",
            status=503,
            error_type="service_error",
            extra={"exception": str(e)},
            log_level="error"
        )


def api_signup():
    """JSON API endpoint for new user registration."""

    # Check Content-Type header
    content_error = require_json_content_type()
    if content_error:
        return content_error

    # Extract data from JSON
    data = request.get_json()
    if not data:
        invalid_body = request.get_data(as_text=True)
        return api_error(
            "Invalid JSON",
            status=400,
            error_type="invalid_json",
            extra={
                'content_type': request.content_type,
                'body_length': len(invalid_body),
                'body_preview': _sanitize_invalid_json_body(invalid_body)
            }
        )

    # Validate input data
    error = validate_login_data(data)
    if error:
        return api_error(
            error,
            status=400,
            error_type="validation_failed",
            extra={
                'user_email': data.get('email')
            }
        )

    # Extract input data
    email = data["email"]
    password = data["password"]

    # Create user via Firebase Authentication Service
    (user, error) = create_firebase_user(email, password)
    if error:
        return api_error(
            error,
            status=400,
            error_type="user_creation_failed",
            extra={
                'user_email': email
            }
        )

    # Save new user information to database
    uid = user.uid
    user_info = {"email": email, "role": "user"}
    save_user_info(uid, user_info)

    logger.info("API signup successful", extra={
        'user_id': uid,
        'endpoint': '/api/signup',
        'method': 'POST'
    })

    return jsonify({"message": "User created successfully", "uid": uid}), 201