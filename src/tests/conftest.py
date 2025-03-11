from src.db.main import get_session
from src import app
from src.auth.dependencies import AccessTokenBearer, RefreshTokenBearer, RoleChecker
from unittest.mock import AsyncMock, Mock
import pytest
from fastapi.testclient import TestClient

mock_session_object = AsyncMock()
mock_user_service_object = Mock()
mock_book_service_object = Mock()

def get_mock_session():
    yield mock_session_object

atb = AccessTokenBearer()
rtb = RefreshTokenBearer()
role_checker = RoleChecker(allowed_roles=["ADMIN"])

app.dependency_overrides[get_session] = get_mock_session
app.dependency_overrides[role_checker] = Mock()
app.dependency_overrides[rtb] = Mock()

@pytest.fixture
def mock_session():
    return mock_session_object

@pytest.fixture
def mock_user_service():
    return mock_user_service_object

@pytest.fixture
def mock_book_service():
    return mock_book_service_object

@pytest.fixture
def test_client():
    return TestClient(app=app)
