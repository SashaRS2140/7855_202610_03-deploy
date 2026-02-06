from tinydb import TinyDB, Query

class DatabaseRepository:
    def __init__(self, db_path):
        self.db = TinyDB(db_path)
        self.users = self.db.table("users")
        self.profiles = self.db.table('profiles')
        self.User = Query()

    def get_all_profiles(self):
        """Returns all user profiles."""
        return self.profiles.all()

    def get_profile(self, username):
        """Finds a single user by username."""
        result = self.profiles.search(self.User.username == username)
        return result[0] if result else None

    def save_profile(self, data):
        """Upserts a user profile."""
        username = data.get('username')
        self.profiles.upsert(data, self.User.username == username)

    def delete_profile(self, username):
        self.profiles.remove(self.User.username == username)

    def delete_user(self, username):
        self.users.remove(self.User.username == username)

    def get_user(self, username):
        result = self.users.search(self.User.username == username)
        return result[0] if result else None

    def save_user(self, data):
        self.users.upsert(data, self.User.username == data["username"])