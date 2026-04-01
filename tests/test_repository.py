import pytest
from unittest.mock import MagicMock

def test_get_user_info_success(mock_firestore_client, repo):
    """Test successful user info retrieval."""
    # Setup mock document
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {
        "user_info": {"email": "test_email@gmail.com", "first_name": "Johnny", "last_name": "Test", "role": "user"}
    }
    mock_firestore_client['user_profiles'].document.return_value.get.return_value = mock_doc

    result = repo.get_user_info("test_uid", "email")
    assert result == "test_email@gmail.com"
    
    # Verify Firestore interactions
    mock_firestore_client['user_profiles'].document.assert_called_once_with("test_uid")
    mock_firestore_client['user_profiles'].document.return_value.get.assert_called_once()


def test_get_user_info_no_doc(mock_firestore_client, repo):
    """Test user info retrieval when document doesn't exist."""
    mock_doc = MagicMock()
    mock_doc.exists = False
    mock_firestore_client['user_profiles'].document.return_value.get.return_value = mock_doc

    result = repo.get_user_info("test_uid", "email")
    assert result is None
    
    # Verify Firestore interactions
    mock_firestore_client['user_profiles'].document.assert_called_once_with("test_uid")
    mock_firestore_client['user_profiles'].document.return_value.get.assert_called_once()


def test_get_user_info_no_data(mock_firestore_client, repo):
    """Test user info retrieval when document has no user_info field."""
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {}
    mock_firestore_client['user_profiles'].document.return_value.get.return_value = mock_doc

    result = repo.get_user_info("test_uid", "email")
    assert result is None
    
    # Verify Firestore interactions
    mock_firestore_client['user_profiles'].document.assert_called_once_with("test_uid")
    mock_firestore_client['user_profiles'].document.return_value.get.assert_called_once()


def test_get_user_info_no_field(mock_firestore_client, repo):
    """Test user info retrieval when requested field doesn't exist."""
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {
        "user_info": {"first_name": "Johnny", "last_name": "Test", "role": "user"}
    }
    mock_firestore_client['user_profiles'].document.return_value.get.return_value = mock_doc

    result = repo.get_user_info("test_uid", "email")
    assert result is None
    
    # Verify Firestore interactions
    mock_firestore_client['user_profiles'].document.assert_called_once_with("test_uid")
    mock_firestore_client['user_profiles'].document.return_value.get.assert_called_once()


def test_get_all_user_info_success(mock_firestore_client, repo):
    """Test successful retrieval of all user info."""
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {
        "user_info": {"email": "test_email@gmail.com", "first_name": "Johnny", "last_name": "Test", "role": "user"}
    }
    mock_firestore_client['user_profiles'].document.return_value.get.return_value = mock_doc

    result = repo.get_all_user_info("test_uid")
    assert result == {
        "email": "test_email@gmail.com",
        "first_name": "Johnny",
        "last_name": "Test",
        "role": "user"
    }
    
    # Verify Firestore interactions
    mock_firestore_client['user_profiles'].document.assert_called_once_with("test_uid")
    mock_firestore_client['user_profiles'].document.return_value.get.assert_called_once()


def test_get_all_user_info_no_doc(mock_firestore_client, repo):
    """Test all user info retrieval when document doesn't exist."""
    mock_doc = MagicMock()
    mock_doc.exists = False
    mock_firestore_client['user_profiles'].document.return_value.get.return_value = mock_doc

    result = repo.get_all_user_info("test_uid")
    assert result is None
    
    # Verify Firestore interactions
    mock_firestore_client['user_profiles'].document.assert_called_once_with("test_uid")
    mock_firestore_client['user_profiles'].document.return_value.get.assert_called_once()


def test_get_all_user_info_no_data(mock_firestore_client, repo):
    """Test all user info retrieval when document has no user_info field."""
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {}
    mock_firestore_client['user_profiles'].document.return_value.get.return_value = mock_doc

    result = repo.get_all_user_info("test_uid")
    assert result is None
    
    # Verify Firestore interactions
    mock_firestore_client['user_profiles'].document.assert_called_once_with("test_uid")
    mock_firestore_client['user_profiles'].document.return_value.get.assert_called_once()


def test_get_cube_user_success(mock_firestore_client, repo):
    """Test successful cube user retrieval."""
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {"user uid": "test_user_uid"}
    mock_firestore_client['cubes'].document.return_value.get.return_value = mock_doc

    result = repo.get_cube_user("test_cube_uuid")
    assert result == "test_user_uid"
    
    # Verify Firestore interactions
    mock_firestore_client['cubes'].document.assert_called_once_with("test_cube_uuid")
    mock_firestore_client['cubes'].document.return_value.get.assert_called_once()


def test_get_cube_user_no_doc(mock_firestore_client, repo):
    """Test cube user retrieval when document doesn't exist."""
    mock_doc = MagicMock()
    mock_doc.exists = False
    mock_firestore_client['cubes'].document.return_value.get.return_value = mock_doc

    result = repo.get_cube_user("test_cube_uuid")
    assert result is None
    
    # Verify Firestore interactions
    mock_firestore_client['cubes'].document.assert_called_once_with("test_cube_uuid")
    mock_firestore_client['cubes'].document.return_value.get.assert_called_once()


def test_get_cube_user_no_data(mock_firestore_client, repo):
    """Test cube user retrieval when document has no user uid field."""
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {}
    mock_firestore_client['cubes'].document.return_value.get.return_value = mock_doc

    result = repo.get_cube_user("test_cube_uuid")
    assert result is None
    
    # Verify Firestore interactions
    mock_firestore_client['cubes'].document.assert_called_once_with("test_cube_uuid")
    mock_firestore_client['cubes'].document.return_value.get.assert_called_once()


def test_get_profile_success(mock_firestore_client, repo):
    """Test successful profile retrieval."""
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {
        "current_task": "Meditation",
        "presets": {"Meditation": {"task_color": "#ffaa00", "task_time": 600}},
        "session_history": [{"elapsed_time": 300, "task": "Meditation", "timestamp": "2023-01-01T00:00:00"}],
        "user_info": {"email": "test_email@gmail.com", "first_name": "Johnny", "last_name": "Test", "role": "user"}
    }
    mock_firestore_client['user_profiles'].document.return_value.get.return_value = mock_doc

    result = repo.get_profile("test_uid")
    assert result == {
        "current_task": "Meditation",
        "presets": {"Meditation": {"task_color": "#ffaa00", "task_time": 600}},
        "session_history": [{"elapsed_time": 300, "task": "Meditation", "timestamp": "2023-01-01T00:00:00"}],
        "user_info": {"email": "test_email@gmail.com", "first_name": "Johnny", "last_name": "Test", "role": "user"}
    }
    
    # Verify Firestore interactions
    mock_firestore_client['user_profiles'].document.assert_called_once_with("test_uid")
    mock_firestore_client['user_profiles'].document.return_value.get.assert_called_once()


def test_get_profile_no_doc(mock_firestore_client, repo):
    """Test profile retrieval when document doesn't exist."""
    mock_doc = MagicMock()
    mock_doc.exists = False
    mock_firestore_client['user_profiles'].document.return_value.get.return_value = mock_doc

    result = repo.get_profile("test_uid")
    assert result is None
    
    # Verify Firestore interactions
    mock_firestore_client['user_profiles'].document.assert_called_once_with("test_uid")
    mock_firestore_client['user_profiles'].document.return_value.get.assert_called_once()


def test_get_task_preset_success(mock_firestore_client, repo):
    """Test successful task preset retrieval."""
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {
        "presets": {"Meditation": {"task_color": "#ffaa00", "task_time": 600}}
    }
    mock_firestore_client['user_profiles'].document.return_value.get.return_value = mock_doc

    result = repo.get_task_preset("test_uid", "Meditation")
    assert result == {"task_color": "#ffaa00", "task_time": 600}
    
    # Verify Firestore interactions
    mock_firestore_client['user_profiles'].document.assert_called_once_with("test_uid")
    mock_firestore_client['user_profiles'].document.return_value.get.assert_called_once()


def test_get_task_preset_no_doc(mock_firestore_client, repo):
    """Test task preset retrieval when document doesn't exist."""
    mock_doc = MagicMock()
    mock_doc.exists = False
    mock_firestore_client['user_profiles'].document.return_value.get.return_value = mock_doc

    result = repo.get_task_preset("test_uid", "Meditation")
    assert result is None
    
    # Verify Firestore interactions
    mock_firestore_client['user_profiles'].document.assert_called_once_with("test_uid")
    mock_firestore_client['user_profiles'].document.return_value.get.assert_called_once()


def test_get_task_preset_no_presets(mock_firestore_client, repo):
    """Test task preset retrieval when document has no presets field."""
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {}
    mock_firestore_client['user_profiles'].document.return_value.get.return_value = mock_doc

    result = repo.get_task_preset("test_uid", "Meditation")
    assert result is None
    
    # Verify Firestore interactions
    mock_firestore_client['user_profiles'].document.assert_called_once_with("test_uid")
    mock_firestore_client['user_profiles'].document.return_value.get.assert_called_once()


def test_get_task_preset_no_preset(mock_firestore_client, repo):
    """Test task preset retrieval when requested preset doesn't exist."""
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {
        "presets": {"Meditation": {"task_color": "#ffaa00", "task_time": 600}}
    }
    mock_firestore_client['user_profiles'].document.return_value.get.return_value = mock_doc

    result = repo.get_task_preset("test_uid", "NonExistentTask")
    assert result is None
    
    # Verify Firestore interactions
    mock_firestore_client['user_profiles'].document.assert_called_once_with("test_uid")
    mock_firestore_client['user_profiles'].document.return_value.get.assert_called_once()


def test_get_all_task_presets_success(mock_firestore_client, repo):
    """Test successful retrieval of all task presets."""
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {
        "presets": {"Meditation": {"task_color": "#ffaa00", "task_time": 600}}
    }
    mock_firestore_client['user_profiles'].document.return_value.get.return_value = mock_doc

    result = repo.get_all_task_presets("test_uid")
    assert result == {"Meditation": {"task_color": "#ffaa00", "task_time": 600}}
    
    # Verify Firestore interactions
    mock_firestore_client['user_profiles'].document.assert_called_once_with("test_uid")
    mock_firestore_client['user_profiles'].document.return_value.get.assert_called_once()


def test_get_all_task_presets_no_doc(mock_firestore_client, repo):
    """Test all task presets retrieval when document doesn't exist."""
    mock_doc = MagicMock()
    mock_doc.exists = False
    mock_firestore_client['user_profiles'].document.return_value.get.return_value = mock_doc

    result = repo.get_all_task_presets("test_uid")
    assert result is None
    
    # Verify Firestore interactions
    mock_firestore_client['user_profiles'].document.assert_called_once_with("test_uid")
    mock_firestore_client['user_profiles'].document.return_value.get.assert_called_once()


def test_get_all_task_presets_no_presets(mock_firestore_client, repo):
    """Test all task presets retrieval when document has no presets field."""
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {}
    mock_firestore_client['user_profiles'].document.return_value.get.return_value = mock_doc

    result = repo.get_all_task_presets("test_uid")
    assert result is None
    
    # Verify Firestore interactions
    mock_firestore_client['user_profiles'].document.assert_called_once_with("test_uid")
    mock_firestore_client['user_profiles'].document.return_value.get.assert_called_once()


def test_get_current_task_success(mock_firestore_client, repo):
    """Test successful current task retrieval."""
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {"current_task": "Meditation"}
    mock_firestore_client['user_profiles'].document.return_value.get.return_value = mock_doc

    result = repo.get_current_task("test_uid")
    assert result == "Meditation"
    
    # Verify Firestore interactions
    mock_firestore_client['user_profiles'].document.assert_called_once_with("test_uid")
    mock_firestore_client['user_profiles'].document.return_value.get.assert_called_once()


def test_get_current_task_no_doc(mock_firestore_client, repo):
    """Test current task retrieval when document doesn't exist."""
    mock_doc = MagicMock()
    mock_doc.exists = False
    mock_firestore_client['user_profiles'].document.return_value.get.return_value = mock_doc

    result = repo.get_current_task("test_uid")
    assert result is None
    
    # Verify Firestore interactions
    mock_firestore_client['user_profiles'].document.assert_called_once_with("test_uid")
    mock_firestore_client['user_profiles'].document.return_value.get.assert_called_once()


def test_get_current_task_no_current_task(mock_firestore_client, repo):
    """Test current task retrieval when document has no current_task field."""
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {}
    mock_firestore_client['user_profiles'].document.return_value.get.return_value = mock_doc

    result = repo.get_current_task("test_uid")
    assert result is None
    
    # Verify Firestore interactions
    mock_firestore_client['user_profiles'].document.assert_called_once_with("test_uid")
    mock_firestore_client['user_profiles'].document.return_value.get.assert_called_once()


def test_get_session_success(mock_firestore_client, repo):
    """Test successful session retrieval."""
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {
        "session_history": [{"elapsed_time": 300, "task": "Meditation", "timestamp": "2023-01-01T00:00:00"}]
    }
    mock_firestore_client['user_profiles'].document.return_value.get.return_value = mock_doc

    result = repo.get_session("test_uid")
    assert result == {"elapsed_time": 300, "task": "Meditation", "timestamp": "2023-01-01T00:00:00"}
    
    # Verify Firestore interactions
    mock_firestore_client['user_profiles'].document.assert_called_once_with("test_uid")
    mock_firestore_client['user_profiles'].document.return_value.get.assert_called_once()


def test_get_session_no_doc(mock_firestore_client, repo):
    """Test session retrieval when document doesn't exist."""
    mock_doc = MagicMock()
    mock_doc.exists = False
    mock_firestore_client['user_profiles'].document.return_value.get.return_value = mock_doc

    result = repo.get_session("test_uid")
    assert result is None
    
    # Verify Firestore interactions
    mock_firestore_client['user_profiles'].document.assert_called_once_with("test_uid")
    mock_firestore_client['user_profiles'].document.return_value.get.assert_called_once()


def test_save_session_interaction(mock_firestore_client, repo):
    """Test that save_session calls Firestore correctly."""
    # Setup mock document reference
    mock_doc = MagicMock()
    mock_firestore_client['user_profiles'].document.return_value = mock_doc

    # Call the function
    repo.save_session("test_uid", "Meditation", 300, "#ffaa00")

    # Verify interactions
    mock_firestore_client['user_profiles'].document.assert_called_with("test_uid")
    mock_doc.update.assert_called_once()

    # Check the data passed to update
    call_args = mock_doc.update.call_args[0][0]
    assert 'session_history' in call_args
    # ArrayUnion wraps the session data
    from google.cloud.firestore import ArrayUnion
    assert isinstance(call_args['session_history'], ArrayUnion)
    session_data = call_args['session_history']._values[0]


def test_save_cube_uuid_interaction(mock_firestore_client, repo):
    """Test that save_cube_uuid calls Firestore correctly."""
    mock_doc = MagicMock()
    mock_firestore_client['cubes'].document.return_value = mock_doc

    repo.save_cube_uuid("test_uid", "test_cube_uuid")

    mock_firestore_client['cubes'].document.assert_called_with("test_cube_uuid")
    mock_doc.set.assert_called_once_with({"user uid": "test_uid"}, merge=True)


def test_get_session_no_presets(mock_firestore_client, repo):
    # Override mock behavior
    mock_firestore_client['user_profiles'].document.return_value.get.return_value.exists = True
    mock_firestore_client['user_profiles'].document.return_value.get.return_value.to_dict.return_value = {}
    result = repo.get_session("test_uid")
    assert result is None


def test_save_user_info(mock_firestore_client, repo):
    mock_firestore_client['user_profiles'].document.return_value.get.return_value.to_dict.return_value = {
        "current_task": "Meditation",
        "presets": {"Meditation": {"task_color": "#ffaa00", "task_time": 600}},
        "session_history": [{"elapsed_time": 300, "task": "Meditation", "timestamp": "2023-01-01T00:00:00"}],
        "user_info": {"email": "test_email@gmail.com", "first_name": "Johnny", "last_name": "Test", "role": "user"}
    }
    user_info = {"test_field": "test_value"}
    repo.save_user_info("test_uid", user_info)


def test_save_cube_uuid(mock_firestore_client, repo):
    repo.save_cube_uuid("test_uid", "test_cube_uuid")


def test_update_task_preset(mock_firestore_client, repo):
    preset_data = {"task_color": "#ffbb00", "task_time": 900}
    repo.update_task_preset("test_uid", "study_task", preset_data)


def test_update_task_preset_first_preset(mock_firestore_client, repo):
    mock_firestore_client['user_profiles'].document.return_value.get.return_value.to_dict.return_value = {}
    preset_data = {"task_color": "#ffbb00", "task_time": 900}
    repo.update_task_preset("test_uid", "study_task", preset_data)


def test_delete_task_preset(mock_firestore_client, repo):
    repo.delete_task_preset("test_uid", "study_task")


def test_set_current_task(mock_firestore_client, repo):
    mock_firestore_client['user_profiles'].document.return_value.get.return_value.to_dict.return_value = {
        "current_task": "Meditation",
        "presets": {"Meditation": {"task_color": "#ffaa00", "task_time": 600}},
        "session_history": [{"elapsed_time": 300, "task": "Meditation", "timestamp": "2023-01-01T00:00:00"}],
        "user_info": {"email": "test_email@gmail.com", "first_name": "Johnny", "last_name": "Test", "role": "user"}
    }
    repo.set_current_task("test_uid", "study_task")


def test_save_session(mock_firestore_client, repo):
    repo.save_session("test_uid", "Meditation", 600)


def test_save_session_with_color(mock_firestore_client, repo):
    repo.save_session("test_uid", "Meditation", 600, "#ffaa00")





