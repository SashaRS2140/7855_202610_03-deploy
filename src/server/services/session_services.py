from bcrypt import hashpw, checkpw, gensalt

class SessionService:
    def __init__(self, repository):
        self.repo = repository

    def validate_user(self, username, password):
        user = self.repo.get_user(username)
        if not user:
            return False

        return checkpw(
            password.encode("utf-8"),
            user["password_hash"].encode("utf-8")
        )

    def get_dashboard_data(self):
        """Prepares data for the dashboard."""
        return self.repo.get_all_profiles()

    def get_user_profile(self, username):
        return self.repo.get_profile(username) or {}

    def update_user_profile(self, username, form_data):
        """Validates and sanitizes input before saving."""
        f_name = form_data.get("first_name", "")
        l_name = form_data.get("last_name", "")
        s_id = form_data.get("student_id", "")

        s_id = str(s_id)

        if not all([f_name, l_name, s_id]) or not s_id.strip().isdigit():
            return {"error": "Invalid input: All fields required and ID must be numeric."}

        clean_data = {
            "username": username,
            "first_name": f_name.strip().capitalize(),
            "last_name": l_name.strip().capitalize(),
            "student_id": s_id.strip()
        }

        self.repo.save_profile(clean_data)
        return {"success": True}

    def delete_user_profile(self, username):
        return self.repo.delete_profile(username)

    def create_user(self, username, password):
        password_hash = hashpw(
            password.encode("utf-8"),
            gensalt()
        ).decode("utf-8")

        self.repo.save_user({
            "username": username,
            "password_hash": password_hash
        })

    def delete_user(self, username):
        self.repo.delete_profile(username)
        return self.repo.delete_user(username)
