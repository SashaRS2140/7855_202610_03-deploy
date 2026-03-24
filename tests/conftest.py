# Add this at the VERY TOP, before any other imports
import sys
from unittest.mock import MagicMock, patch
import types

# Early mock to prevent firebase.py from running
mock_user_profiles = MagicMock(name="mock_user_profiles")
mock_cubes = MagicMock(name="mock_cubes")
mock_user_doc = MagicMock()
mock_cube_doc = MagicMock()
mock_user_profiles.document.return_value = mock_user_doc
mock_cubes.document.return_value = mock_cube_doc

mock_user_doc.get.return_value.exists = True
mock_user_doc.get.return_value.to_dict.return_value = {
    "current_task": "Meditation",
    "presets": {"Meditation": {"task_color": "#ffaa00", "task_time": 600}},
    "session_history": [{"elapsed_time": 300, "task": "Meditation", "timestamp": "2023-01-01T00:00:00"}],
    "user_info": {"email": "test_email@gmail.com", "first_name": "Johnny", "last_name": "Test", "role": "user"}
}
mock_cube_doc.get.return_value.exists = False
mock_cube_doc.get.return_value.to_dict.return_value = {}

fake_firebase = types.ModuleType("firebase")
fake_firebase.user_profiles = mock_user_profiles
fake_firebase.cubes = mock_cubes
sys.modules["firebase"] = fake_firebase

# Prevent real init
patch('firebase_admin.initialize_app').start()

# Now your original imports and fixtures
import pytest
import importlib
from unittest.mock import MagicMock



@pytest.fixture
def client(monkeypatch):
    """Flask test client fixture with TESTING enabled."""
    monkeypatch.setenv("CUBE_API_KEY", "test-key")

    app_module = importlib.import_module("run")
    app = app_module.create_app()
    app.config.update(TESTING=True)

    app.timer = MagicMock(name="mock_timer")

    with app.test_client() as test_client:
        yield test_client


@pytest.fixture
def mock_firestore():
    """Return the global mock firestore objects for per-test overrides."""
    return {
        "user_profiles": mock_user_profiles,
        "user_doc_ref": mock_user_doc,
        "user_snapshot": mock_user_doc.get.return_value,
        "cubes": mock_cubes,
        "cube_doc_ref": mock_cube_doc,
        "cube_snapshot": mock_cube_doc.get.return_value,
    }
    """Patch JWT verification to return a known test uid by default."""
    verify_mock = MagicMock(return_value={"uid": "test_user_123"})
    monkeypatch.setattr("decorators.auth.auth.verify_id_token", verify_mock)
    return verify_mock


@pytest.fixture
def repo():
    """Reload repository module to ensure fresh mocks."""
    import src.server.utils.repository
    return importlib.reload(src.server.utils.repository)

@pytest.fixture
def mock_task_control(monkeypatch):
    monkeypatch.setattr(
        "src.server.routes.cube_routes.get_cube_user",
        lambda cube_uuid: "test_uid"
    )

    monkeypatch.setattr(
        "src.server.routes.cube_routes.get_current_task",
        lambda uid: "Meditation"
    )

    monkeypatch.setattr(
        "src.server.routes.cube_routes.get_task_preset",
        lambda uid, task: {"task_time": 600}
    )
