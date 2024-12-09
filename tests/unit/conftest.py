import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock, AsyncMock
from auth import verify_token 
from db import get_mongo_client
import os
from bson import ObjectId

# Mock user data
MOCK_USER = {
    "id": "test_user_id",
    "email_addresses": [{"email_address": "test@example.com"}],
}

async def mock_verify_token(request):
    return {"user_id": "test_user_id", "user": MOCK_USER}

@pytest.fixture(autouse=True)
def mock_environment():
    """Set up test environment variables"""
    os.environ["TESTING"] = "true"
    os.environ["CLERK_KEY"] = "test_key"
    yield
    os.environ.pop("TESTING", None)
    os.environ.pop("CLERK_KEY", None)

@pytest.fixture(autouse=True)
def mock_clerk():
    """Mock Clerk API calls"""
    with patch('auth.Clerk') as mock_clerk:
        mock_clerk_instance = MagicMock()
        mock_clerk_instance.users.get.return_value = MOCK_USER
        mock_clerk.return_value = mock_clerk_instance
        yield mock_clerk_instance

@pytest.fixture(autouse=True)
def mock_dependencies():
    app.dependency_overrides = {
        verify_token: lambda: {"user_id": "test_user_id", "user": MOCK_USER},
        get_mongo_client: lambda: AsyncMock(),
    }
    yield
    app.dependency_overrides = {}

@pytest.fixture
def client():
    """Create test client"""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def mock_thread_id():
    return str(ObjectId())

@pytest.fixture
def mock_user_id():
    return str(ObjectId())

@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.brade_dev = AsyncMock()
    db.brade_dev.document_indices = AsyncMock()
    return db