from flask import session
from src.server.utils import auth
from unittest.mock import MagicMock


def test_create_firebase_user_success(monkeypatch):
    class FakeUser:
        uid = "123"

    monkeypatch.setattr(
        "src.server.utils.auth.auth.create_user",
        lambda email, password: FakeUser()
    )

    user, error = auth.create_firebase_user("test@test.com", "password")

    assert user is not None
    assert error is None


def test_create_firebase_user_email_error(monkeypatch):
    from firebase_admin._auth_utils import EmailAlreadyExistsError
    error = EmailAlreadyExistsError(
        "Email already exists",
        cause=None,
        http_response=None
    )

    monkeypatch.setattr(
        "src.server.utils.auth.auth.create_user",
        MagicMock(side_effect=error)
    )

    user, err = auth.create_firebase_user("test@test.com", "password")

    assert user is None
    assert err == "A user with this email already exists."


def test_create_firebase_user_firebase_error(monkeypatch):
    from firebase_admin.exceptions import FirebaseError
    error = FirebaseError(
        "Error code",
        "Some firebase issue",
        cause=None,
        http_response=None
    )

    monkeypatch.setattr(
        "src.server.utils.auth.auth.create_user",
        MagicMock(side_effect=error)
    )

    user, err = auth.create_firebase_user("test@test.com", "password")

    assert user is None
    assert "Firebase error" in err


def test_create_firebase_user_unexpected_error(monkeypatch):
    monkeypatch.setattr(
        "src.server.utils.auth.auth.create_user",
        MagicMock(side_effect=Exception("Something weird"))
    )

    user, err = auth.create_firebase_user("test@test.com", "password")

    assert user is None
    assert "Unexpected error" in err


def test_get_current_user_success(client):
    with client.application.test_request_context():
        session["logged_in"] = True
        session["uid"] = "test_uid"

        result = auth.get_current_user()

    assert result == "test_uid"


def test_get_current_user_logged_out(client):
    with client.application.test_request_context():
        session["logged_in"] = False
        session["uid"] = "test_uid"

        result = auth.get_current_user()

    assert result is None