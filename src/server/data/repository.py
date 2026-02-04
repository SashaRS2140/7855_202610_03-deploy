from tinydb import TinyDB, Query

class DatabaseRepository:
    def __init__(self, db_path):
        self.db = TinyDB(db_path)
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