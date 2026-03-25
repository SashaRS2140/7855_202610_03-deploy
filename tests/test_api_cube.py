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


def test_task_control_non_json_data(client, mock_cube_request):
    # Arrange
    url = "http://localhost:5000/api/task/control"
    headers = {"X-API-Key": "test-key"}
    payload = {"action": "start"}

    # Act
    response = client.post(url, data=payload, headers=headers)

    # Assert
    assert response.status_code == 415
    assert response.get_json()["error"] == "Content-Type must be application/json"


def test_task_control_no_data(client, mock_cube_request):
    # Arrange
    url = "http://localhost:5000/api/task/control"
    headers = {"X-API-Key": "test-key"}
    payload = {}

    # Act
    response = client.post(url, json=payload, headers=headers)

    # Assert
    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid JSON"


def test_task_control_no_current_task(client, mock_cube_request, monkeypatch):
    # Arrange
    url = "http://localhost:5000/api/task/control"
    headers = {"X-API-Key": "test-key"}
    payload = {"action": "start"}

    monkeypatch.setattr(
        "src.server.blueprints.api_cube.routes.get_current_task",
        lambda uid: None
    )

    # Act
    response = client.post(url, json=payload, headers=headers)

    # Assert
    assert response.status_code == 400
    assert response.get_json()["error"] == "Current task not set"


def test_task_control_start_success(client, mock_cube_request):
    # Arrange
    url = "http://localhost:5000/api/task/control"
    headers = {"X-API-Key": "test-key"}
    payload = {"action": "start"}

    # Act
    response = client.post(url, json=payload, headers=headers)

    # Assert
    assert response.status_code == 200
    assert response.get_json()["message"] == "Meditation task started"
    client.application.timer.start.assert_called_once()


def test_task_control_stop_success(client, mock_cube_request):
    # Arrange
    url = "http://localhost:5000/api/task/control"
    headers = {"X-API-Key": "test-key"}
    payload = {"action": "stop", "elapsed_seconds": 300}

    # Act
    response = client.post(url, json=payload, headers=headers)

    # Assert
    assert response.status_code == 200
    assert response.get_json()["message"] == "Meditation task stopped. 5m:0s of session time logged."
    client.application.timer.stop.assert_called_once()


def test_task_control_stop_success_with_overtime(client, mock_cube_request):
    # Arrange
    url = "http://localhost:5000/api/task/control"
    headers = {"X-API-Key": "test-key"}
    payload = {"action": "stop", "elapsed_seconds": 900}

    # Act
    response = client.post(url, json=payload, headers=headers)

    # Assert
    assert response.status_code == 200
    assert response.get_json()["message"] == "Meditation task stopped. 10m:0s of session time + 5m:0s of extra session time logged."
    client.application.timer.stop.assert_called_once()


def test_task_control_reset_success(client, mock_cube_request):
    # Arrange
    url = "http://localhost:5000/api/task/control"
    headers = {"X-API-Key": "test-key"}
    payload = {"action": "reset"}

    # Act
    response = client.post(url, json=payload, headers=headers)

    # Assert
    assert response.status_code == 200
    assert response.get_json()["message"] == "Meditation task reset"
    assert response.get_json()["task_name"] == "Meditation"
    assert response.get_json()["task_time"] == 600
    client.application.timer.reset.assert_called_once()






