import os
import hmac
from functools import wraps
from firebase_admin import auth
from flask import request, redirect, url_for, session
from src.server.logging_config import get_logger
from src.server.utils.api_response import api_error

logger = get_logger(__name__)

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "uid" not in session:
            logger.warning("Unauthenticated access attempt", extra={
                'endpoint': request.path,
                'method': request.method,
                'error_type': 'not_authenticated'
            })
            return redirect(url_for("auth.login"))
        return f(*args, uid=session["uid"], **kwargs)
    return wrapper


def require_jwt(f):
    """Decorator to require JWT authentication for API endpoints.

    Verifies the JWT token from the Authorization header and injects
    the user ID into the route function as a keyword argument 'uid'.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return api_error(
                "Missing Authorization header",
                status=401,
                error_type="missing_authorization_header",
                extra={
                    'auth_type': 'jwt'
                }
            )

        # Check for "Bearer " prefix
        if not auth_header.startswith("Bearer "):
            return api_error(
                "Invalid Authorization header format",
                status=401,
                error_type="invalid_authorization_format",
                extra={
                    'auth_type': 'jwt'
                }
            )

        token = auth_header.split(" ")[1]

        try:
            # Verify the JWT token using Firebase Admin SDK
            decoded_token = auth.verify_id_token(token)
            uid = decoded_token["uid"]
            # Inject uid into the route function
            return f(*args, uid=uid, **kwargs)
        except Exception:
            return api_error(
                "Invalid or expired token",
                status=401,
                error_type="invalid_or_expired_token",
                extra={
                    'auth_type': 'jwt'
                }
            )
    return decorated_function


def require_api_key(f):
    """Decorator to require API key authentication for device endpoints.
    
    Expected header: X-API-Key: <actual_cube_uuid>
    The X-API-Key header should contain the cube's UUID for authentication.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get the expected key from environment
        expected_key = os.environ.get("CUBE_API_KEY")

        if not expected_key:
            return api_error(
                "API key not configured on server",
                status=500,
                error_type="api_key_not_configured"
            )

        # Get the provided key from request headers
        provided_key = request.headers.get("X-API-Key")

        if not provided_key:
            return api_error(
                "Missing X-API-Key header",
                status=401,
                error_type="missing_api_key",
                extra={
                    'auth_type': 'api_key'
                }
            )

        # Compare keys (constant-time comparison to prevent timing attacks)
        if not hmac.compare_digest(provided_key, expected_key):
            return api_error(
                "Unauthorized",
                status=401,
                error_type="invalid_api_key",
                extra={
                    'auth_type': 'api_key'
                }
            )

        # Security: X-API-Key header should contain the actual cube_uuid
        # Not the API key itself. Extract from request if provided.
        cube_uuid = request.headers.get("X-Cube-UUID", provided_key)

        # Allow the route to execute with the cube UUID
        return f(*args, cube_uuid=cube_uuid, **kwargs)
    return decorated_function


