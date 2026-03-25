import pytest

def test_get_user_info_success(mock_firestore, repo):
    result = repo.get_user_info("test_uid", "email")
    assert result == "test_email@gmail.com"


def test_get_user_info_no_doc(mock_firestore, repo):
    # Override mock behavior
    mock_firestore["user_doc_ref"].get.return_value.exists = False
    result = repo.get_user_info("test_uid", "email")
    assert result is None


def test_get_user_info_no_data(mock_firestore, repo):
    # Override mock behavior
    mock_firestore["user_doc_ref"].get.return_value.exists = True
    mock_firestore["user_doc_ref"].get.return_value.to_dict.return_value = {}
    result = repo.get_user_info("test_uid", "email")
    assert result is None


def test_get_user_info_no_field(mock_firestore, repo):
    # Override mock behavior
    mock_firestore["user_doc_ref"].get.return_value.to_dict.return_value = {
        "current_task": "Meditation",
        "presets": {"Meditation": {"task_color": "#ffaa00", "task_time": 600}},
        "session_history": [{"elapsed_time": 300, "task": "Meditation", "timestamp": "2023-01-01T00:00:00"}],
        "user_info": {"email": "test_email@gmail.com", "first_name": "Johnny", "last_name": "Test", "role": "user"}
    }
    result = repo.get_user_info("test_uid", "test")
    assert result is None


def test_get_all_user_info_success(mock_firestore, repo):
    result = repo.get_all_user_info("test_uid")
    assert result == {
        "email": "test_email@gmail.com",
        "first_name": "Johnny",
        "last_name": "Test",
        "role": "user"
    }


def test_get_all_user_info_no_doc(mock_firestore, repo):
    # Override mock behavior
    mock_firestore["user_doc_ref"].get.return_value.exists = False
    result = repo.get_all_user_info("test_uid")
    assert result is None


def test_get_all_user_info_no_data(mock_firestore, repo):
    # Override mock behavior
    mock_firestore["user_doc_ref"].get.return_value.exists = True
    mock_firestore["user_doc_ref"].get.return_value.to_dict.return_value = {}
    result = repo.get_all_user_info("test_uid")
    assert result is None


def test_get_cube_user_success(mock_firestore, repo):
    # Override mock behavior
    result = repo.get_cube_user("test_uid")
    assert result == "test_user_uid"


def test_get_cube_user_no_doc(mock_firestore, repo):
    # Override mock behavior
    mock_firestore["cube_doc_ref"].get.return_value.exists = False
    result = repo.get_cube_user("test_uid")
    assert result is None


def test_get_cube_user_no_data(mock_firestore, repo):
    # Override mock behavior
    mock_firestore["cube_doc_ref"].get.return_value.exists = True
    mock_firestore["cube_doc_ref"].get.return_value.to_dict.return_value = {}
    result = repo.get_cube_user("test_uid")
    assert result is None


def test_get_profile_success(mock_firestore, repo):
    # Override mock behavior
    mock_firestore["user_doc_ref"].get.return_value.exists = True
    mock_firestore["user_doc_ref"].get.return_value.to_dict.return_value = {
        "current_task": "Meditation",
        "presets": {"Meditation": {"task_color": "#ffaa00", "task_time": 600}},
        "session_history": [{"elapsed_time": 300, "task": "Meditation", "timestamp": "2023-01-01T00:00:00"}],
        "user_info": {"email": "test_email@gmail.com", "first_name": "Johnny", "last_name": "Test", "role": "user"}
    }
    result = repo.get_profile("test_uid")
    assert result == {
        "current_task": "Meditation",
        "presets": {"Meditation": {"task_color": "#ffaa00", "task_time": 600}},
        "session_history": [{"elapsed_time": 300, "task": "Meditation", "timestamp": "2023-01-01T00:00:00"}],
        "user_info": {"email": "test_email@gmail.com", "first_name": "Johnny", "last_name": "Test", "role": "user"}
    }


def test_get_profile_no_doc(mock_firestore, repo):
    # Override mock behavior
    mock_firestore["user_doc_ref"].get.return_value.exists = False
    result = repo.get_profile("test_uid")
    assert result is None


def test_get_task_preset_success(mock_firestore, repo):
    mock_firestore["user_doc_ref"].get.return_value.exists = True
    result = repo.get_task_preset("test_uid", "Meditation")
    assert result == {"task_color": "#ffaa00", "task_time": 600}


def test_get_task_preset_no_doc(mock_firestore, repo):
    # Override mock behavior
    mock_firestore["user_doc_ref"].get.return_value.exists = False
    result = repo.get_task_preset("test_uid", "Meditation")
    assert result is None


def test_get_task_preset_no_presets(mock_firestore, repo):
    # Override mock behavior
    mock_firestore["user_doc_ref"].get.return_value.exists = True
    mock_firestore["user_doc_ref"].get.return_value.to_dict.return_value = {}
    result = repo.get_task_preset("test_uid", "Meditation")
    assert result is None


def test_get_task_preset_no_preset(mock_firestore, repo):
    # Override mock behavior
    mock_firestore["user_doc_ref"].get.return_value.to_dict.return_value = {
        "current_task": "Meditation",
        "presets": {"Meditation": {"task_color": "#ffaa00", "task_time": 600}},
        "session_history": [{"elapsed_time": 300, "task": "Meditation", "timestamp": "2023-01-01T00:00:00"}],
        "user_info": {"email": "test_email@gmail.com", "first_name": "Johnny", "last_name": "Test", "role": "user"}
    }
    result = repo.get_task_preset("test_uid", "test")
    assert result is None


def test_get_all_task_presets_success(mock_firestore, repo):
    result = repo.get_all_task_presets("test_uid")
    assert result == {"Meditation": {"task_color": "#ffaa00", "task_time": 600}}


def test_get_all_task_presets_no_doc(mock_firestore, repo):
    # Override mock behavior
    mock_firestore["user_doc_ref"].get.return_value.exists = False
    result = repo.get_all_task_presets("test_uid")
    assert result is None


def test_get_all_task_presets_no_presets(mock_firestore, repo):
    # Override mock behavior
    mock_firestore["user_doc_ref"].get.return_value.exists = True
    mock_firestore["user_doc_ref"].get.return_value.to_dict.return_value = {}
    result = repo.get_all_task_presets("test_uid")
    assert result is None


def test_get_current_task_success(mock_firestore, repo):
    mock_firestore["user_doc_ref"].get.return_value.to_dict.return_value = {
        "current_task": "Meditation",
        "presets": {"Meditation": {"task_color": "#ffaa00", "task_time": 600}},
        "session_history": [{"elapsed_time": 300, "task": "Meditation", "timestamp": "2023-01-01T00:00:00"}],
        "user_info": {"email": "test_email@gmail.com", "first_name": "Johnny", "last_name": "Test", "role": "user"}
    }
    result = repo.get_current_task("test_uid")
    assert result == "Meditation"


def test_get_current_task_no_doc(mock_firestore, repo):
    # Override mock behavior
    mock_firestore["user_doc_ref"].get.return_value.exists = False
    result = repo.get_current_task("test_uid")
    assert result is None


def test_get_current_task_no_presets(mock_firestore, repo):
    # Override mock behavior
    mock_firestore["user_doc_ref"].get.return_value.exists = True
    mock_firestore["user_doc_ref"].get.return_value.to_dict.return_value = {}
    result = repo.get_current_task("test_uid")
    assert result is None


def test_get_session_success(mock_firestore, repo):
    mock_firestore["user_doc_ref"].get.return_value.to_dict.return_value = {
        "current_task": "Meditation",
        "presets": {"Meditation": {"task_color": "#ffaa00", "task_time": 600}},
        "session_history": [{"elapsed_time": 300, "task": "Meditation", "timestamp": "2023-01-01T00:00:00"}],
        "user_info": {"email": "test_email@gmail.com", "first_name": "Johnny", "last_name": "Test", "role": "user"}
    }
    result = repo.get_session("test_uid")
    assert result == [{"elapsed_time": 300, "task": "Meditation", "timestamp": "2023-01-01T00:00:00"}]


def test_get_session_no_doc(mock_firestore, repo):
    # Override mock behavior
    mock_firestore["user_doc_ref"].get.return_value.exists = False
    result = repo.get_session("test_uid")
    assert result is None


def test_get_session_no_presets(mock_firestore, repo):
    # Override mock behavior
    mock_firestore["user_doc_ref"].get.return_value.exists = True
    mock_firestore["user_doc_ref"].get.return_value.to_dict.return_value = {}
    result = repo.get_session("test_uid")
    assert result is None


def test_save_user_info(mock_firestore, repo):
    mock_firestore["user_doc_ref"].get.return_value.to_dict.return_value = {
        "current_task": "Meditation",
        "presets": {"Meditation": {"task_color": "#ffaa00", "task_time": 600}},
        "session_history": [{"elapsed_time": 300, "task": "Meditation", "timestamp": "2023-01-01T00:00:00"}],
        "user_info": {"email": "test_email@gmail.com", "first_name": "Johnny", "last_name": "Test", "role": "user"}
    }
    user_info = {"test_field": "test_value"}
    repo.save_user_info("test_uid", user_info)


def test_save_cube_uuid(mock_firestore, repo):
    repo.save_cube_uuid("test_uid", "test_cube_uuid")


def test_update_task_preset(mock_firestore, repo):
    preset_data = {"task_color": "#ffbb00", "task_time": 900}
    repo.update_task_preset("test_uid", "study_task", preset_data)


def test_update_task_preset_first_preset(mock_firestore, repo):
    mock_firestore["user_doc_ref"].get.return_value.to_dict.return_value = {}
    preset_data = {"task_color": "#ffbb00", "task_time": 900}
    repo.update_task_preset("test_uid", "study_task", preset_data)


def test_delete_task_preset(mock_firestore, repo):
    repo.delete_task_preset("test_uid", "study_task")


def test_set_current_task(mock_firestore, repo):
    mock_firestore["user_doc_ref"].get.return_value.to_dict.return_value = {
        "current_task": "Meditation",
        "presets": {"Meditation": {"task_color": "#ffaa00", "task_time": 600}},
        "session_history": [{"elapsed_time": 300, "task": "Meditation", "timestamp": "2023-01-01T00:00:00"}],
        "user_info": {"email": "test_email@gmail.com", "first_name": "Johnny", "last_name": "Test", "role": "user"}
    }
    repo.set_current_task("test_uid", "study_task")


def test_save_session(mock_firestore, repo):
    repo.save_session("test_uid", "Meditation", 600)


def test_save_session_with_color(mock_firestore, repo):
    repo.save_session("test_uid", "Meditation", 600, "#ffaa00")





