import os
import re
from flask import jsonify, request
from firebase_admin import auth
from firebase_admin._auth_utils import EmailAlreadyExistsError
from firebase_admin.exceptions import FirebaseError
from bcrypt import hashpw, checkpw, gensalt


##########################################################################
###                        HELPER FUNCTIONS                            ###
##########################################################################


#WEB_API_KEY = os.environ.get("FIREBASE_WEB_API_KEY")
WEB_API_KEY = "AIzaSyAyuzcT80Cgh91lC2-eQLOtZyRHl0ipN68"


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

    # Pattern Validation for task_color
    task_color = data.get("task_color", "")

    if task_color:
        if not isinstance(task_color, str) or not re.compile(r"^#[0-9a-fA-F]{6}$").fullmatch(task_color):
            errors.append("Task color must be a valid hex RGB string (e.g., '#0000ff')")

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


def validate_profile(data):
    # Check that all fields are provided and non-empty
    first_name = data.get("first_name", "")
    last_name = data.get("last_name", "")
    student_id = data.get("student_id", "")
    if not first_name or not last_name or not student_id:
        return "All fields are required."

    student_id = str(student_id)

    # Check that student_id is numeric
    if not student_id.isdigit():
        return "Student ID must be numeric."

    return None


def normalize_profile(data):
    first_name = data.get("first_name", "")
    last_name = data.get("last_name", "")
    student_id = data.get("student_id", "")

    return {
        "first_name": str(first_name).strip().capitalize(),
        "last_name": str(last_name).strip().capitalize(),
        "student_id": str(student_id).strip()
    }


##########################################################################
###                      SessionService CLASS                          ###
##########################################################################


class SessionService:
    def __init__(self, repository):
        self.repo = repository


    def save_user_info(self, uid: str, user_info: dict[str, str]):
        """Saves user information in database."""
        self.repo.save_user_info_data(uid, user_info)


    def get_user_info(self, uid: str, field: str):
        """Reads a specific user information field from the database."""
        return self.repo.get_user_info_data(uid, field)


    def get_all_user_info(self, uid: str):
        """Reads all user information from the database."""
        return self.repo.get_all_user_info_data(uid)


    def save_cube_uuid(self, uid: str, cube_uuid: str):
        self.repo.save_cube_uuid_data(uid, cube_uuid)


    def get_cube_user(self, cube_uuid: str):
        return self.repo.get_cube_user_data(cube_uuid)


    def get_profile(self, uid: str):
        """Reads all user profile data from the database."""
        return self.repo.get_profile_data(uid) or {}


    def get_task_preset(self, uid: str, task_name: str):
        return self.repo.get_task_preset_data(uid, task_name)


    def get_all_task_presets(self, uid: str):
        return self.repo.get_all_task_presets_data(uid)


    def update_task_preset(self, uid: str, task_name: str, preset_data: dict):
        self.repo.update_task_preset_data(uid, task_name, preset_data)


    def delete_task_preset(self, uid: str, task_name: str):
        self.repo.delete_task_preset_data(uid, task_name)


    def set_current_task(self, uid: str, task_name: str):
        self.repo.set_current_task_data(uid, task_name)


    def get_current_task(self, uid: str):
        return self.repo.get_current_task_data(uid)


    def get_session(self, uid: str):
        return self.repo.get_session_data(uid)


    def save_session(self, uid: str, task: str, elapsed_time: int):
        self.repo.save_session_data(uid, task, elapsed_time)


    # -----Below in Progress-----#


    def validate_user(self, uid, password):
        user = self.repo.get_user_data(uid)
        if not user:
            return False

        return checkpw(
            password.encode("utf-8"),
            user["password_hash"].encode("utf-8")
        )


    def save_profile(self, uid, profile_data):
        self.repo.save_profile_data(uid, profile_data)


    def delete_profile(self, uid):
        self.repo.delete_profile_data(uid)


    def get_user(self, uid):
        return self.repo.get_user_data(uid) or {}


    def delete_user(self, uid):
        self.repo.delete_profile_data(uid)
        self.repo.delete_user_data(uid)







