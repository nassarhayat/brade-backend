import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from main import app
from unittest.mock import Mock, patch, ANY
from bson import ObjectId

# Test data
mock_thread_id = str(ObjectId())
mock_user_id = str(ObjectId())

@pytest.fixture
def mock_thread():
    """Mock thread response after creation"""
    return {
        "id": mock_thread_id,
        "created": datetime.utcnow().isoformat(),
        "updated": datetime.utcnow().isoformat(),
        "items": [],
        "total_items": 0,
        "page": 1,
        "page_size": 20
    }

@pytest.fixture
def mock_thread_item():
    return {
        "id": str(ObjectId()),
        "thread_id": mock_thread_id,
        "user_id": mock_user_id,
        "content": "Test content",
        "userType": "user",
        "block": {
            "id": str(ObjectId()),
            "document_id": str(ObjectId()),
            "document_type": "test"
        },
        "context_document_ids": [str(ObjectId())],
        "steps": []
    }

class TestThreadEndpoints:
    def setup_method(self):
        self.headers = {
            "Authorization": "Bearer test_token",
            "Content-Type": "application/json"
        }

    @patch('services.thread_service.create_thread_service')
    def test_create_thread(self, mock_create_service, mock_thread, client):
        # Arrange
        mock_create_service.return_value = mock_thread
        
        # Act
        request_data = {
            "userRequest": "Test request"
        }
        print("\nSending request:")
        print("Headers:", self.headers)
        print("Body:", request_data)
        response = client.post(
            "/threads",
            json=request_data,  # Make sure it's sent in the request body
            headers=self.headers
        )
        
        print("\nResponse status:", response.status_code)
        print("Response body:", response.json())
        
        # Assert
        assert response.status_code == 200

    @patch('routers.threads.get_threads_service')
    def test_get_threads(self, mock_get_service, mock_thread, client):
        # Arrange
        mock_response = {
            "threads": [mock_thread],
            "total": 1,
            "page": 1,
            "page_size": 20
        }
        mock_get_service.return_value = mock_response
        
        # Act
        response = client.get(
            "/threads?page=1&page_size=20",
            headers=self.headers
        )
        # Assert
        assert response.status_code == 200
        assert len(response.json()["threads"]) == 1
        assert response.json()["total"] == 1
        assert response.json()["page_size"] == 20

        mock_get_service.assert_called_once_with(1, 20, ANY)

    @patch('routers.threads.get_thread_service')
    def test_get_thread(self, mock_get_service, mock_thread, client):
        # Arrange
        mock_get_service.return_value = mock_thread
        
        # Act
        response = client.get(
            f"/threads/{mock_thread_id}",
            headers=self.headers
        )
        print("\nResponse body:", response.json())
        # Assert
        assert response.status_code == 200
        assert response.json()["id"] == mock_thread_id
        mock_get_service.assert_called_once_with(mock_thread_id, 1, 20, ANY)

    @patch('routers.threads.get_thread_service')
    def test_get_thread_not_found(self, mock_get_service, client):
        # Arrange
        mock_get_service.return_value = None
        
        # Act
        response = client.get(
            f"/threads/{mock_thread_id}",
            headers=self.headers
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Thread not found"

    @patch('routers.threads.add_thread_item_service')
    def test_add_thread_item(self, mock_add_service, mock_thread_item, client):
        # Arrange
        mock_add_service.return_value = iter([  # Simulate a streaming response
            '{"id": "test_id", "content": "Test content"}'
        ])

        request_data = {
            "content": "Test content",
            "userType": "user",
            "block": {
                "id": str(ObjectId()),
                "document_id": str(ObjectId()),
                "document_type": "test",
                "blockType": "text",
                "data": {}
            },
            "context_document_ids": [str(ObjectId())],
            "steps": []
        }

        # Act
        response = client.post(
            f"/threads/{mock_thread_id}",
            json=request_data,
            headers=self.headers
        )

        # Collect streaming content
        streamed_content = b"".join(response.iter_bytes()).decode()

        # Assert
        assert response.status_code == 200
        assert "Test content" in streamed_content

    def test_invalid_page_size(self, client):
        # Act
        response = client.get(
            "/threads?page=1&page_size=101",
            headers=self.headers
        )
        
        # Assert
        assert response.status_code == 422

    def test_invalid_page_number(self, client):
        # Act
        response = client.get(
            "/threads?page=0&page_size=20",
            headers=self.headers
        )
        
        # Assert
        assert response.status_code == 422