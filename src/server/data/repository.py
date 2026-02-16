import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore import DELETE_FIELD


# Initialize Firebase only once
if not firebase_admin._apps:
    cred = credentials.Certificate("src/server/serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

class Repository:
    def __init__(self):
        self.db = firestore.client()
        # Define references to collections
        self.users = self.db.collection("users")
        self.profiles = self.db.collection("profiles")

    def get_all_profile_data(self):
        """Returns all user profiles as a list of dictionaries."""
        docs = self.profiles.stream()
        # Convert each document snapshot to a dictionary
        return [doc.to_dict() for doc in docs]

    def get_profile_data(self, username):
        """Finds a single user profile by username."""
        # Use the username directly as the document ID
        doc = self.profiles.document(username).get()
        if doc.exists:
            return doc.to_dict()
        return None

    def save_profile_data(self, username, data):
        """Upserts a user profile."""
        # We store the profile nested under a "profile" key to match your old structure,
        # and include the username so the returned object looks like the old TinyDB one.
        payload = {
            "username": username,
            "profile": data
        }
        # set(..., merge=True) acts like an upsert (update if exists, create if not)
        self.profiles.document(username).set(payload, merge=True)

    def delete_profile_data(self, username):
        """Deletes a profile document."""
        self.profiles.document(username).delete()

    def get_user_data(self, username):
        """Gets user auth data (password hash)."""
        doc = self.users.document(username).get()
        if doc.exists:
            return doc.to_dict()
        return None

    def save_user_data(self, data):
        """Saves user auth data."""
        # Assuming 'data' contains a 'username' key
        username = data.get("username")
        if username:
            self.users.document(username).set(data, merge=True)

    def delete_user_data(self, username):
        """Deletes a user auth document."""
        self.users.document(username).delete()

    def get_task_preset_data(self, username, task):
        doc = self.profiles.document(username).get()
        if not doc.exists:
            return None

        presets = doc.to_dict().get("presets")
        if not presets:
            return None

        if not task in presets:
            return None
        return presets.get(task)

    def get_all_task_presets_data(self, username):
        doc = self.profiles.document(username).get()
        if not doc.exists:
            return None

        presets = doc.to_dict().get("presets")
        if not presets:
            return None
        return presets

    def update_task_preset_data(self, username, task, preset_data):
        doc_ref = self.profiles.document(username)
        doc = doc_ref.get()

        if doc.exists:
            presets = doc.to_dict().get("presets", {})
        else:
            presets = {}

        presets[task] = preset_data

        doc_ref.set({"presets": presets}, merge=True)

    def delete_task_preset_data(self, username, task):
        self.profiles.document(username).update({
            f"presets.{task}": DELETE_FIELD
        })
