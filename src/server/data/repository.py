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
        self.cubes = self.db.collection("cubes")


    def save_user_info_data(self, uid: str, user_info: dict[str, str]):
        """Saves user information data."""
        self.user_profiles.document(uid).set({"user_info": user_info}, merge=True)


    def get_user_info_data(self, uid: str, field: str):
        doc = self.user_profiles.document(uid).get()
        if not doc.exists:
            return None

        user_info = doc.to_dict().get("user_info")
        if not user_info:
            return None

        if not field in user_info:
            return None
        return user_info.get(field)


    def get_all_user_info_data(self, uid: str):
        doc = self.user_profiles.document(uid).get()
        if not doc.exists:
            return None

        user_info = doc.to_dict().get("user_info")
        if not user_info:
            return None
        return user_info


    def save_cube_uuid_data(self, uid: str, cube_uuid: str):
        self.cubes.document(cube_uuid).set({"user uid": uid}, merge=True)

    def get_cube_user_data(self, cube_uuid: str):
        doc = self.cubes.document(cube_uuid).get()
        if not doc.exists:
            return None

        uid = doc.to_dict().get("user uid")
        if not uid:
            return None
        return uid


    def get_profile_data(self, uid: str):
        """Finds a single user profile by username."""
        # Use the username directly as the document ID
        doc = self.user_profiles.document(uid).get()
        if doc.exists:
            return doc.to_dict()
        return None


    def get_task_preset_data(self, uid: str, task: str):
        doc = self.user_profiles.document(uid).get()
        if not doc.exists:
            return None

        presets = doc.to_dict().get("presets")
        if not presets:
            return None

        if not task in presets:
            return None
        return presets.get(task)


    def get_all_task_presets_data(self, uid: str):
        doc = self.user_profiles.document(uid).get()
        if not doc.exists:
            return None

        presets = doc.to_dict().get("presets")
        if not presets:
            return None
        return presets


    def update_task_preset_data(self, uid: str, task: str, preset_data: dict):
        doc_ref = self.user_profiles.document(uid)
        doc = doc_ref.get()

        if doc.exists:
            presets = doc.to_dict().get("presets", {})
        else:
            presets = {}

        presets[task] = preset_data

        doc_ref.set({"presets": presets}, merge=True)


    def delete_task_preset_data(self, uid: str, task: str):
        self.user_profiles.document(uid).update({
            f"presets.{task}": DELETE_FIELD
        })


    def set_current_task_data(self, uid: str, task_name: str):
        doc_ref = self.user_profiles.document(uid)
        doc_ref.set({"current_task": task_name}, merge=True)


    def get_current_task_data(self, uid: str):
        doc = self.user_profiles.document(uid).get()
        if not doc.exists:
            return None

        current_task = doc.to_dict().get("current_task")
        if not current_task:
            return None
        return current_task


    def get_session_data(self, uid: str):
        doc = self.user_profiles.document(uid).get()
        if not doc.exists:
            return None

        session_history = doc.to_dict().get("session_history")
        if not session_history:
            return None
        return session_history


    def save_session_data(self, uid: str, task: str, elapsed_time: int):
        doc_ref = self.user_profiles.document(uid)
        data = {"task": task, "elapsed_time": elapsed_time}
        doc_ref.set({"session_history": data}, merge=True)


    # -----Below in Progress-----#


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
