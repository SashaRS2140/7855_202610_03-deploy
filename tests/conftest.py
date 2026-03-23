import sys
import types
import pytest
import importlib
from unittest.mock import MagicMock


@pytest.fixture
def mock_firestore(monkeypatch):
    """Starter Firestore mock fixture.

    This injects a fake `firebase` module before app import so tests do not
    require real Firebase credentials or network access.
    """
    mock_user_profiles = MagicMock(name="mock_user_profiles")
    mock_user_doc_ref = MagicMock(name="mock_user_doc_ref")
    mock_user_snapshot = MagicMock(name="mock_user_snapshot")

    # Default chain used by routes/helpers:
    # db.collection(...).document(...).get()/set()/update()/delete()
    mock_user_profiles.document.return_value = mock_user_doc_ref
    mock_user_doc_ref.get.return_value = mock_user_snapshot

    # Default user profile response.
    mock_user_snapshot.exists = True
    mock_user_snapshot.to_dict.return_value = {
        "current_task": "Meditation",
        "presets": {
            "Meditation": {
            "task_color": "#ffaa00",
            "task_time": 600
            },
            "Relaxation": {
            "task_color": "#ffaa11",
            "task_time": 900
            },
        },
        "session_history": {
            "elapsed_time": 300,
            "task": "Meditation"
        },
        "user_info": {
            "email": "test_email@gmail.com",
            "first_name": "Johnny",
            "last_name": "Test",
            "role": "user"
        }
    }

    mock_cubes = MagicMock(name="mock_cubes")
    mock_cubes_doc_ref = MagicMock(name="mock_cubes_doc_ref")
    mock_cubes_snapshot = MagicMock(name="mock_cubes_snapshot")

    # Default chain used by routes/helpers:
    # db.collection(...).document(...).get()/set()/update()/delete()
    mock_cubes.document.return_value = mock_cubes_doc_ref
    mock_cubes_doc_ref.get.return_value = mock_cubes_snapshot

    # Default cube response.
    mock_cubes_snapshot.exists = True
    mock_cubes_snapshot.to_dict.return_value = {
        "user uid": "test_user_uid"
    }

    fake_firebase_module = types.ModuleType("firebase")
    fake_firebase_module.user_profiles = mock_user_profiles
    fake_firebase_module.cubes = mock_cubes
    monkeypatch.setitem(sys.modules, "firebase", fake_firebase_module)

    return {
        "user_profiles": mock_user_profiles,
        "user_doc_ref": mock_user_doc_ref,
        "user_snapshot": mock_user_snapshot,
        "cubes": mock_cubes,
        "cube_doc_ref": mock_cubes_doc_ref,
        "cube_snapshot": mock_cubes_snapshot,
    }


@pytest.fixture
def client(monkeypatch, mock_firestore):
    """Flask test client fixture with TESTING enabled."""
    monkeypatch.setenv("CUBE_API_KEY", "test-key")

    app_module = importlib.import_module("run")
    app = app_module.create_app()
    app.config.update(TESTING=True)

    app.timer = MagicMock(name="mock_timer")

    with app.test_client() as test_client:
        yield test_client


@pytest.fixture
def mock_firebase_auth(monkeypatch):
    """Patch JWT verification to return a known test uid by default."""
    verify_mock = MagicMock(return_value={"uid": "test_user_123"})
    monkeypatch.setattr("decorators.auth.auth.verify_id_token", verify_mock)
    return verify_mock


@pytest.fixture
def repo(mock_firestore):
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
