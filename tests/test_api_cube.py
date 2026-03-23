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


def test_task_control_wrong_key(client):
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
def test_task_control_valid_key(client):
    # Arrange
    url = "http://localhost:5000/api/task/control"
    headers = {"X-API-Key": "test-sensor-key"}
    pass