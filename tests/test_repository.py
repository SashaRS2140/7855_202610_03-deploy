import pytest
from src.server.utils.repository import save_user_info

@pytest.mark.parametrize("uid, email, role, expected",
    [
        # Valid partition
        ("breid@my.bcit.ca", "password1", "password1", []),
    ]
)
def test_save_user_info(uid, email, role, expected):
    user_info = {"email": email, "role": role}
    assert save_user_info(uid, user_info) == expected