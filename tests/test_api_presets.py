def test_api_get_preset_no_auth(client):
    # Arrange
    url = "http://localhost:5000/api/profile/preset/meditation"

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 401
    data = response.get_json()
    assert "error" in data


def test_api_get_preset_no_task_name_in_route(client):
    # Arrange
    url = "http://localhost:5000/api/profile/preset"

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 405


def test_api_get_preset_bad_token_format(client):
    # Arrange
    url = "http://localhost:5000/api/profile/preset/meditation"
    headers = {'Authorization': 'NotBearer xyz'}

    # Act
    response = client.get(url, headers=headers)

    # Assert
    assert response.status_code == 401


def test_api_get_preset_invalid_token(client, mock_firebase_auth):
    # Arrange
    url = "http://localhost:5000/api/profile/preset/meditation"
    headers = {"Authorization": "Bearer invalid_jwt_token"}
    mock_firebase_auth.side_effect = Exception("Invalid token")

    # Act
    response = client.get(url, headers=headers)

    # Assert
    assert response.status_code == 401
    mock_firebase_auth.assert_called_once()


def test_api_get_preset_no_presets(client, mock_firebase_auth, mock_presets_repository, monkeypatch):
    # Arrange
    url = "http://localhost:5000/api/profile/preset/all"
    headers = {"Authorization": "Bearer valid_jwt_token"}
    monkeypatch.setattr(
        "src.server.blueprints.api_presets.routes.get_all_task_presets",
        lambda uid: {}
    )

    # Act
    response = client.get(url, headers=headers)

    # Assert
    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "No presets configured."
    mock_firebase_auth.assert_called_once()


def test_api_get_preset_get_all_success(client, mock_firebase_auth, mock_presets_repository):
    # Arrange
    url = "http://localhost:5000/api/profile/preset/all"
    headers = {"Authorization": "Bearer valid_jwt_token"}

    # Act
    response = client.get(url, headers=headers)

    # Assert
    assert response.status_code == 200
    data = response.get_json()
    assert data["presets"] == {"Meditation": {"task_color": "#ffaa00", "task_time": 600}}
    mock_firebase_auth.assert_called_once()


def test_api_get_preset_not_found(client, mock_firebase_auth, mock_presets_repository, monkeypatch):
    # Arrange
    url = "http://localhost:5000/api/profile/preset/bad_test"
    headers = {"Authorization": "Bearer valid_jwt_token"}
    monkeypatch.setattr(
        "src.server.blueprints.api_presets.routes.get_task_preset",
        lambda uid, task_name: None
    )

    # Act
    response = client.get(url, headers=headers)

    # Assert
    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "Preset not found"
    mock_firebase_auth.assert_called_once()


def test_api_get_preset_success(client, mock_firebase_auth, mock_presets_repository):
    # Arrange
    url = "http://localhost:5000/api/profile/preset/meditation"
    headers = {"Authorization": "Bearer valid_jwt_token"}

    # Act
    response = client.get(url, headers=headers)

    # Assert
    assert response.status_code == 200
    data = response.get_json()
    assert data["Meditation"] == {"task_color": "#ffaa00", "task_time": 600}
    mock_firebase_auth.assert_called_once()


def test_api_create_preset_content_error(client, mock_firebase_auth, mock_presets_repository):
    # Arrange
    url = "http://localhost:5000/api/profile/preset"
    headers = {"Authorization": "Bearer valid_jwt_token"}
    payload = {"study": {"task_color": "#ffaa00", "task_time": 900}}

    # Act
    response = client.post(url, json=payload, headers=headers)

    # Assert
    assert response.status_code == 415
    mock_firebase_auth.assert_called_once()