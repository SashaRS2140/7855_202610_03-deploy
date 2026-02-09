from tinydb import TinyDB, Query

class DatabaseRepository:
    def __init__(self, db_path):
        self.db = TinyDB(db_path)
        self.users = self.db.table("users")
        self.profiles = self.db.table('profiles')
        self.User = Query()

    def get_all_profile_data(self):
        """Returns all user profiles."""
        return self.profiles.all()

    def get_profile_data(self, username):
        """Finds a single user by username."""
        result = self.profiles.search(self.User.username == username)
        return result[0] if result else None

    def save_profile_data(self, username, data):
        """Upserts a user profile."""
        if self.profiles.search(self.User.username == username):
            self.profiles.update({"profile": data}, self.User.username == username)
        else:
            self.profiles.insert({"username": username, "profile": data})

    def delete_profile_data(self, username):
        self.profiles.remove(self.User.username == username)

    def delete_user_data(self, username):
        self.users.remove(self.User.username == username)

    def get_user_data(self, username):
        result = self.users.search(self.User.username == username)
        return result[0] if result else None

    def save_user_data(self, data):
        self.users.upsert(data, self.User.username == data["username"])