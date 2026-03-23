import pytest

def test_get_all_user_info_success(mock_firestore, repo):
    result = repo.get_all_user_info("test_uid")

    assert result == {
        "email": "test_email@gmail.com",
        "first_name": "Johnny",
        "last_name": "Test",
        "role": "user"
    }


def test_get_all_user_info_no_doc(mock_firestore, repo):
    # Override mock behavior
    mock_firestore["user_doc_ref"].get.return_value.exists = False
    result = repo.get_all_user_info("test_uid")

    assert result is None


def test_get_all_user_info_no_data(mock_firestore, repo):
    # Override mock behavior
    mock_firestore["user_doc_ref"].get.return_value.to_dict.return_value = {}
    result = repo.get_all_user_info("test_uid")

    assert result is None


def test_get_cube_user_success(mock_firestore, repo):
    result = repo.get_cube_user("test_uid")

    assert result == "test_user_uid"


def test_get_cube_user_no_doc(mock_firestore, repo):
    # Override mock behavior
    mock_firestore["cube_doc_ref"].get.return_value.exists = False
    result = repo.get_cube_user("test_uid")

    assert result is None


def test_get_cube_user_no_data(mock_firestore, repo):
    # Override mock behavior
    mock_firestore["cube_doc_ref"].get.return_value.to_dict.return_value = {}
    result = repo.get_cube_user("test_uid")

    assert result is None