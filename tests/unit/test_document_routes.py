import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from main import app
from datetime import datetime, UTC

@pytest.fixture
def client():
    return TestClient(app)

@pytest.mark.asyncio
async def test_create_document_endpoint(client):
    # Arrange
    test_doc = {
        "title": "Test Document",
        "content": {
            "type": "doc",
            "content": [{"type": "text", "text": "Test Content"}]
        },
        "metadata": {}
    }
    
    mock_response = {
        "id": "test-123",
        "title": test_doc["title"],
        "content": test_doc["content"],
        "metadata": test_doc["metadata"],
        "created_at": datetime.now(UTC).isoformat(),
        "updated_at": datetime.now(UTC).isoformat()
    }
    
    mock_forward = AsyncMock(return_value=mock_response)
    
    with patch('routers.documents.forward_to_node', mock_forward):
        # Act
        response = client.post("/documents", json=test_doc)
        
        # Assert
        assert response.status_code == 200
        assert response.json()["title"] == test_doc["title"]
        mock_forward.assert_called_once_with("POST", "documents", test_doc)

@pytest.mark.asyncio
async def test_search_documents_endpoint(client):
    # Print debug info to see what's happening
    print("\nDebugging search endpoint test:")
    
    # Arrange
    mock_search_results = {
        "total": 1,
        "documents": [{
            "id": "test-123",
            "title": "Test Doc",
            "content": {
                "type": "doc",
                "content": [{"type": "text", "text": "Test Content"}]
            },
            "metadata": {},
            "created_at": datetime.now(UTC).isoformat(),
            "updated_at": datetime.now(UTC).isoformat(),
            "version": 1,
            "score": 1.0
        }]
    }
    
    mock_search = AsyncMock(return_value=mock_search_results)
    print(f"Mock search results: {mock_search_results}")
    
    # Create a proper MongoDB client mock
    mock_indices = MagicMock()  # Use MagicMock for non-async properties
    mock_db = MagicMock()
    mock_db.document_indices = mock_indices
    mock_client = MagicMock()
    mock_client.brade_dev = mock_db
    
    with patch('services.document_service.search_documents', mock_search), \
         patch('db.get_mongo_client', return_value=mock_client):
        # Act
        request_data = {
            "query": "test",
            "limit": 10,
            "skip": 0
        }
        print(f"Search query: {request_data}")
        
        response = client.post("/documents/search", json=request_data)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        # Assert
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["total"] == 1
        assert len(response_data["documents"]) == 1
        document = response_data["documents"][0]
        assert document["id"] == "test-123"
        assert document["title"] == "Test Doc"
        assert document["score"] == 1.0
        
        # Verify search_documents service was called correctly
        mock_search.assert_called_once_with(
            query="test",
            document_type=None,
            tags=None,
            limit=10,
            skip=0,
            client=mock_client
        )

@pytest.mark.asyncio
async def test_get_document_endpoint(client):
    # Arrange
    test_doc = {
        "id": "test-123",
        "title": "Test Document",
        "content": {
            "type": "doc",
            "content": [{"type": "text", "text": "Test Content"}]
        },
        "metadata": {},
        "created_at": datetime.now(UTC).isoformat(),
        "updated_at": datetime.now(UTC).isoformat()
    }
    
    mock_forward = AsyncMock(return_value=test_doc)
    
    with patch('routers.documents.forward_to_node', mock_forward):
        # Act
        response = client.get("/documents/test-123")
        
        # Assert
        assert response.status_code == 200
        assert response.json()["id"] == test_doc["id"]
        mock_forward.assert_called_once_with("GET", "documents/test-123")