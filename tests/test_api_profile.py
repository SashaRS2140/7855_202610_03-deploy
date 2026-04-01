from unittest.mock import MagicMock


def test_api_get_profile_no_auth(client):
    # Arrange
    url = "http://localhost:5000/api/profile"

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 401
    data = response.get_json()
    assert "error" in data


def test_api_get_profile_bad_token_format(client):
    # Arrange
    url = "http://localhost:5000/api/profile"
    headers = {'Authorization': 'NotBearer xyz'}

    # Act
    response = client.get(url, headers=headers)

    # Assert
    assert response.status_code == 401


def test_api_get_profile_success(client, mock_firebase_auth, repo, mock_firestore_client):
    # Arrange
    url = "http://localhost:5000/api/profile"
    headers = {"Authorization": "Bearer valid_jwt_token"}

    # Mock user profile document with full profile data
    mock_user_doc = MagicMock()
    mock_user_doc.exists = True
    mock_user_doc.to_dict.return_value = {
        "current_task": "Meditation",
        "presets": {"Meditation": {"task_color": "#ffaa00", "task_time": 600}},
        "session_history": [{"elapsed_time": 300, "task": "Meditation", "timestamp": "2023-01-01T00:00:00"}],
        "user_info": {"email": "test_email@gmail.com", "first_name": "Johnny", "last_name": "Test", "role": "user"}
    }
    mock_firestore_client['user_profiles'].document.return_value.get.return_value = mock_user_doc

    # Act
    response = client.get(url, headers=headers)

    # Assert
    assert response.status_code == 200
    data = response.get_json()
    assert data["profile"] == {
        "current_task": "Meditation",
        "presets": {"Meditation": {"task_color": "#ffaa00", "task_time": 600}},
        "session_history": [{"elapsed_time": 300, "task": "Meditation", "timestamp": "2023-01-01T00:00:00"}],
        "user_info": {"email": "test_email@gmail.com", "first_name": "Johnny", "last_name": "Test", "role": "user"}
    }
    mock_firebase_auth.assert_called_once()


def test_api_get_user_info_no_info(client, mock_firebase_auth, repo, mock_firestore_client):
    # Arrange
    url = "http://localhost:5000/api/profile/user_info/all"
    headers = {"Authorization": "Bearer valid_jwt_token"}

    # Mock user profile document without user_info
    mock_user_doc = MagicMock()
    mock_user_doc.exists = True
    mock_user_doc.to_dict.return_value = {}  # No user_info
    mock_firestore_client['user_profiles'].document.return_value.get.return_value = mock_user_doc

    # Act
    response = client.get(url, headers=headers)

    # Assert
    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "No information added."
    mock_firebase_auth.assert_called_once()