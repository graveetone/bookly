import pytest

from src.auth.schemas import UserCreateModel

BASE_URL = "/api/v1/auth"


def test_user_creation(mock_session, mock_user_service, test_client):
    signup_data = {
        "username": "test",
        "email": "test_username@e.mail",
        "first_name": "Firstname",
        "last_name": "Lasttest",
        "password": "test123"
    }
    test_client.post(
        url=f"{BASE_URL}/signup",
        json=signup_data,
    )

    assert mock_user_service.user_exists_called_once_with(signup_data['email'], mock_session)
    assert mock_user_service.create_user_called_once_with(UserCreateModel(**signup_data), mock_session)
