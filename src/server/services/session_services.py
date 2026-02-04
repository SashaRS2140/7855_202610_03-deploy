class SessionService:
    def __init__(self, repository):
        self.repo = repository

    def validate_user(self, username, password):
        """Example login logic."""
        # In a real app, check hashed passwords here.
        # For now, we use your dummy check.
        return username == "student" and password == "secret"

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