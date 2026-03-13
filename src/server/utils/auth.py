from flask import session
from firebase_admin import auth
from firebase_admin.exceptions import FirebaseError
from firebase_admin._auth_utils import EmailAlreadyExistsError


def create_firebase_user(email: str, password: str):
    try:
        user = auth.create_user(
            email=email,
            password=password
        )
        return user, None

    except EmailAlreadyExistsError:
        return None, "A user with this email already exists."

    except FirebaseError as e:
        # Catch other Firebase auth-related errors
        return None, f"Firebase error: {e}"

    except Exception as e:
        # Catch any unexpected errors
        return None, f"Unexpected error: {e}"


def get_current_user():
    """Return the currently logged-in uid (or None).

    Uses session data set during `/login`. This keeps all login checks
    consistent in one place.
    """
    if not session.get("logged_in"):
        return None
    return session.get("uid")