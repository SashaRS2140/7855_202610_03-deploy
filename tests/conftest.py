import importlib
import sys
import types
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_firestore(monkeypatch):
    """Starter Firestore mock fixture.

    This injects a fake `firebase` module before app import so tests do not
    require real Firebase credentials or network access.
    """
    mock_user_profiles = MagicMock(name="mock_user_profiles")
    mock_doc_ref = MagicMock(name="mock_doc_ref")
    mock_snapshot = MagicMock(name="mock_snapshot")

    # Default chain used by routes/helpers:
    # db.collection(...).document(...).get()/set()/update()/delete()
    mock_user_profiles.document.return_value = mock_doc_ref
    mock_doc_ref.get.return_value = mock_snapshot

    # Default user profile response.
    mock_snapshot.exists = True
    mock_snapshot.to_dict.return_value = {
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
        "mock_cubes": mock_cubes,
        "doc_ref": mock_doc_ref,
        "snapshot": mock_snapshot,
    }


@pytest.fixture
def client(monkeypatch, mock_firestore):
    """Flask test client fixture with TESTING enabled."""
    monkeypatch.setenv("CUBE_API_KEY", "test-sensor-key")

    app_module = importlib.import_module("run")
    app = app_module.create_app()
    app.config.update(TESTING=True)

    with app.test_client() as test_client:
        yield test_client


@pytest.fixture
def mock_firebase_auth(monkeypatch):
    """Patch JWT verification to return a known test uid by default."""
    verify_mock = MagicMock(return_value={"uid": "test_user_123"})
    monkeypatch.setattr("decorators.auth.auth.verify_id_token", verify_mock)
    return verify_mock

@pytest.fixture
def mock_require_api_key(monkeypatch):
    verify_mock = MagicMock(return_value={"uid": "test_cube_uuid"})
    monkeypatch.setattr("decorators.auth.require_api_key", verify_mock)
    return verify_mock
