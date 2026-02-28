import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore import DELETE_FIELD


# Initialize Firebase only once
if not firebase_admin._apps:
    cred = credentials.Certificate("src/server/serviceAccountKey.json")
    firebase_admin.initialize_app(cred)


##########################################################################
###                        Repository CLASS                            ###
##########################################################################


class Repository:
    def __init__(self):
        self.db = firestore.client()
        # Define references to collections
        self.user_profiles = self.db.collection("user_profiles")


    def save_user_info_data(self, uid: str, user_info: dict[str, str]):
        """Saves user information data."""
        self.user_profiles.document(uid).set({"user_info": user_info}, merge=True)


    def get_profile_data(self, uid):
        """Finds a single user profile by username."""
        # Use the username directly as the document ID
        doc = self.user_profiles.document(uid).get()
        if doc.exists:
            return doc.to_dict()
        return None


    def get_task_preset_data(self, uid, task):
        doc = self.user_profiles.document(uid).get()
        if not doc.exists:
            return None

        presets = doc.to_dict().get("presets")
        if not presets:
            return None

        if not task in presets:
            return None
        return presets.get(task)


    def get_all_task_presets_data(self, uid):
        doc = self.user_profiles.document(uid).get()
        if not doc.exists:
            return None

        presets = doc.to_dict().get("presets")
        if not presets:
            return None
        return presets


    def update_task_preset_data(self, uid, task, preset_data):
        doc_ref = self.user_profiles.document(uid)
        doc = doc_ref.get()

        if doc.exists:
            presets = doc.to_dict().get("presets", {})
        else:
            presets = {}

        presets[task] = preset_data

        doc_ref.set({"presets": presets}, merge=True)


    # -----Below in Progress-----#

    def get_all_profile_data(self):
        """Returns all user profiles as a list of dictionaries."""
        docs = self.user_profiles.stream()
        # Convert each document snapshot to a dictionary
        return [doc.to_dict() for doc in docs]


    def save_profile_data(self, uid, data):
        """Upserts a user profile."""
        # We store the profile nested under a "profile" key to match your old structure,
        # and include the username so the returned object looks like the old TinyDB one.
        payload = {"profile": data}
        # set(..., merge=True) acts like an upsert (update if exists, create if not)
        self.user_profiles.document(uid).set(payload, merge=True)


    def delete_profile_data(self, uid):
        """Deletes a profile document."""
        self.user_profiles.document(uid).delete()


    def get_user_data(self, uid):
        """Gets user auth data (password hash)."""
        doc = self.user_profiles.document(uid).get()
        if doc.exists:
            return doc.to_dict()
        return None


    def save_user_data(self, data):
        """Saves user auth data."""
        # Assuming 'data' contains a 'uid' key
        uid = data.get("uid")
        if uid:
            self.user_profiles.document(uid).set(data, merge=True)


    def delete_user_data(self, uid):
        """Deletes a user auth document."""
        self.user_profiles.document(uid).delete()


    def delete_task_preset_data(self, uid, task):
        self.user_profiles.document(uid).update({
            f"presets.{task}": DELETE_FIELD
        })


    def set_current_task_data(self, uid, task_name):
        doc_ref = self.user_profiles.document(uid)
        doc_ref.set({"current_task": task_name}, merge=True)


    def get_current_task_data(self, uid):
        doc = self.user_profiles.document(uid).get()
        if not doc.exists:
            return None

        current_task = doc.to_dict().get("current_task")
        if not current_task:
            return None
        return current_task


    def save_session_data(self, uid, task, elapsed_time):
        doc_ref = self.user_profiles.document(uid)
        data = {"task": task, "elapsed_time": elapsed_time}
        doc_ref.set({"session_history": data}, merge=True)


    def get_session_data(self, uid):
        doc = self.user_profiles.document(uid).get()
        if not doc.exists:
            return None

        session_history = doc.to_dict().get("session_history")
        if not session_history:
            return None
        return session_history


    # CURRENTLY UNUSED #
    def set_cube_uuid_data(self, uid, cube_uuid):
        doc_ref = self.user_profiles.document(uid)
        doc_ref.set({"cube_uuid": cube_uuid}, merge=True)

    # CURRENTLY UNUSED #
    def get_cube_uuid_data(self, uid):
        doc = self.user_profiles.document(uid).get()
        if not doc.exists:
            return None

        current_task = doc.to_dict().get("current_task")
        if not current_task:
            return None
        return current_task