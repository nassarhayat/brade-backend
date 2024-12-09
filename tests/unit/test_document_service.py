import pytest
from unittest.mock import Mock, patch, AsyncMock
from services.document_service import (
    get_document, 
    update_document, 
    update_document_indices,
    search_documents
)
import aiohttp
import json
from datetime import datetime

@pytest.fixture
def mock_mongo_client():
    client = Mock()
    # Mock the find_one method to return a proper document structure
    client.brade_dev.document_indices.find_one.return_value = {
        "_id": "mock_id",
        "document_id": "test-doc-123",
        "title": "Test Title",
        "content": "Test Content",
        "document_type": "note",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "tags": ["test"]
    }
    return client

@pytest.fixture
async def mock_session():
    with patch('aiohttp.ClientSession') as mock:
        session = AsyncMock()
        mock.return_value = session
        session.__aenter__.return_value = session
        session.__aexit__.return_value = None
        yield session

@pytest.fixture
def mock_ws(mock_session):
    ws = AsyncMock()
    mock_session.ws_connect.return_value = ws
    return ws

@pytest.fixture
def sample_document():
    return {
        "document_id": "test-doc-123",
        "title": "Test Document",
        "content": "This is a test document content",
        "document_type": "note",
        "tags": ["test", "sample"]
    }

@pytest.mark.asyncio
async def test_get_document(mock_session, mock_ws, sample_document):
    # Arrange
    mock_ws.receive.return_value.type = aiohttp.WSMsgType.TEXT
    mock_ws.receive.return_value.data = json.dumps({
        "type": "document",
        "content": sample_document
    })
    
    with patch('services.document_service.connect_to_repo', return_value=(mock_session, mock_ws)):
        # Act
        result = await get_document("test-doc-123")
        
        # Assert
        assert result == sample_document
        mock_ws.send_json.assert_called_once_with({
            "type": "get_document",
            "documentId": "test-doc-123"
        })

@pytest.mark.asyncio
async def test_update_document(mock_session, mock_ws, sample_document):
    # Arrange
    update_data = {"title": "Updated Title"}
    mock_ws.receive.return_value.type = aiohttp.WSMsgType.TEXT
    mock_ws.receive.return_value.data = '{"type": "success"}'
    
    with patch('services.document_service.connect_to_repo', return_value=(mock_session, mock_ws)):
        # Act
        result = await update_document("test-doc-123", update_data)
        
        # Assert
        assert result is True
        mock_ws.send_json.assert_called_once_with({
            "type": "update_document",
            "documentId": "test-doc-123",
            "content": update_data
        })

@pytest.mark.asyncio
async def test_update_document_indices(mock_mongo_client, sample_document):
    # Arrange
    mock_mongo_client.brade_dev.document_indices.update_one.return_value.modified_count = 1
    
    # Act
    result = await update_document_indices(
        sample_document["document_id"],
        sample_document,
        mock_mongo_client
    )
    
    # Assert
    assert result is not None
    assert result["document_id"] == sample_document["document_id"]
    mock_mongo_client.brade_dev.document_indices.update_one.assert_called_once()

@pytest.mark.asyncio
async def test_search_documents(mock_mongo_client, sample_document):
    # Arrange
    mock_db = Mock()
    mock_mongo_client.get_default_database.return_value = mock_db
    
    mock_collection = Mock()
    mock_db.document_indices = mock_collection
    
    # Create a mock cursor that implements async iterator
    class AsyncCursorMock:
        def __init__(self, documents):
            self.documents = documents
            self._index = 0
            
        def sort(self, *args, **kwargs):
            return self
            
        def skip(self, *args, **kwargs):
            return self
            
        def limit(self, *args, **kwargs):
            return self
            
        def __aiter__(self):
            return self
            
        async def __anext__(self):
            try:
                document = self.documents[self._index]
                self._index += 1
                return {**document, "score": 1.0}  # Add score to the document
            except IndexError:
                raise StopAsyncIteration
    
    # Create cursor with sample documents
    mock_cursor = AsyncCursorMock([sample_document])
    mock_collection.find.return_value = mock_cursor
    
    # Mock the async count_documents method
    async def mock_count_documents(*args, **kwargs):
        return 1
    mock_collection.count_documents = mock_count_documents
    
    # Mock get_document to return the full document
    with patch('services.document_service.get_document') as mock_get_doc:
        mock_get_doc.return_value = sample_document
        
        # Act
        result = await search_documents(
            query="test",
            client=mock_mongo_client
        )
    
    # Assert
    assert result["total"] == 1
    assert len(result["documents"]) == 1
    assert result["documents"][0]["score"] == 1.0  # Verify score is present
    mock_collection.find.assert_called_once()
    
    # Verify the search criteria
    search_criteria = mock_collection.find.call_args[0][0]
    assert "$text" in search_criteria
    assert search_criteria["$text"]["$search"] == "test" 