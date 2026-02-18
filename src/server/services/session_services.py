from bcrypt import hashpw, checkpw, gensalt

class SessionService:
    def __init__(self, repository):
        self.repo = repository

    def validate_user(self, username, password):
        user = self.repo.get_user_data(username)
        if not user:
            return False

        return checkpw(
            password.encode("utf-8"),
            user["password_hash"].encode("utf-8")
        )

    def get_all_profiles(self):
        """Prepares data for the dashboard."""
        return self.repo.get_all_profile_data()

    def get_profile(self, username):
        return self.repo.get_profile_data(username) or {}

    def validate_profile(self, data):
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

    def normalize_profile(self, data):
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")
        student_id = data.get("student_id", "")

        return {
            "first_name": str(first_name).strip().capitalize(),
            "last_name": str(last_name).strip().capitalize(),
            "student_id": str(student_id).strip()
        }

    def save_profile(self, username, profile_data):
        self.repo.save_profile_data(username, profile_data)

    def delete_profile(self, username):
        self.repo.delete_profile_data(username)

    def create_user(self, username, password):
        # Check if user already exists to prevent overwriting
        if self.repo.get_user_data(username):
            return False  # Or raise an error

        password_hash = hashpw(
            password.encode("utf-8"),
            gensalt()
        ).decode("utf-8")

        self.repo.save_user_data({
            "username": username,
            "password_hash": password_hash
        })
        return True

    def get_user(self, username):
        return self.repo.get_user_data(username) or {}

    def delete_user(self, username):
        self.repo.delete_profile_data(username)
        self.repo.delete_user_data(username)

    def get_task_preset(self, username, task_name):
        return self.repo.get_task_preset_data(username, task_name)

    def get_all_task_presets(self, username):
        return self.repo.get_all_task_presets_data(username)

    def update_task_preset(self, username, task_name, preset_data):
        self.repo.update_task_preset_data(username, task_name, preset_data)

    def delete_task_preset(self, username, task_name):
        self.repo.delete_task_preset_data(username, task_name)

    def set_current_task(self, username, task_name):
        self.repo.set_current_task_data(username, task_name)

    def get_current_task(self, username):
        return self.repo.get_current_task_data(username)

    def save_session(self, username, task, elapsed_time):
        self.repo.save_session_data(username, task, elapsed_time)

    def get_session(self, username):
        return self.repo.get_session_data(username)
