from unittest.mock import MagicMock


def test_task_control_server_api_key_not_configured(client, monkeypatch):
    # Arrange
    url = "http://localhost:5000/api/task/control"
    monkeypatch.setenv("CUBE_API_KEY", "")

    # Act
    response = client.post(url)

    # Assert
    assert response.status_code == 500
    data = response.get_json()
    assert data["error"] == "API key not configured on server"


def test_task_control_no_api_key(client):
    # Arrange
    url = "http://localhost:5000/api/task/control"

    # Act
    response = client.post(url)

    # Assert
    assert response.status_code == 401
    data = response.get_json()
    assert data["error"] == "Missing X-API-Key header"


def test_task_control_wrong_key(client, monkeypatch):
    # Arrange
    url = "http://localhost:5000/api/task/control"
    headers = {"X-API-Key": "wrong-key"}

    # Act
    response = client.post(url, headers=headers)

    # Assert
    assert response.status_code == 401
    data = response.get_json()
    assert data["error"] == "Unauthorized"


### NOT FINISHED ###
def test_task_control_valid_key(client, monkeypatch):
    # Arrange
    url = "http://localhost:5000/api/task/control"
    headers = {"X-API-Key": "test-key"}
    payload = {"action": "start"}

    # Act
    response = client.post(url, json=payload, headers=headers)

    # Assert
    #assert response.status_code == 200
    data = response.get_json()
    assert data["error"] == "Cube not registered with user account"
    #assert data["message"] == "Meditation task started"


def test_task_control_start(client, monkeypatch):
    # Arrange
    url = "http://localhost:5000/api/task/control"
    headers = {"X-API-Key": "test-key"}
    payload = {"action": "start"}

    monkeypatch.setattr(
        "src.server.blueprints.api_cube.routes.get_cube_user",
        lambda cube_uuid: "test_uid"
    )
    monkeypatch.setattr(
        "src.server.blueprints.api_cube.routes.get_current_task",
        lambda uid: "Meditation"
    )
    monkeypatch.setattr(
        "src.server.blueprints.api_cube.routes.get_task_preset",
        lambda uid, task: {"task_time": 600}
    )

    # Act
    response = client.post(url, json=payload, headers=headers)

    # Assert
    assert response.status_code == 200
    assert response.get_json()["message"] == "Meditation task started"
    client.application.timer.start.assert_called_once()


def test_task_control_cube_not_registered(client, monkeypatch):
    # Arrange
    url = "http://localhost:5000/api/task/control"
    headers = {"X-API-Key": "test-key"}
    payload = {"action": "start"}

    monkeypatch.setattr(
        "src.server.blueprints.api_cube.routes.get_cube_user",
        lambda cube_uuid: None
    )

    # Act
    response = client.post(url, json=payload, headers=headers)

    # Assert
    assert response.status_code == 401
    assert response.get_json()["error"] == "Cube not registered with user account"



