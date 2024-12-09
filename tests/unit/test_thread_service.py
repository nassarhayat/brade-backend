import pytest
from unittest.mock import Mock, patch
from bson import ObjectId
from services.thread_service import (
    create_thread_service,
    get_threads_service,
    get_thread_service,
    add_thread_item_service
)
from models.thread import ThreadItemModel, BlockModel, UserType

# Test data
mock_thread_id = str(ObjectId())
mock_user_id = str(ObjectId())

@pytest.fixture
def mock_client():
    client = Mock()
    client.brade_dev = Mock()
    client.brade_dev.threads = Mock()
    client.brade_dev.thread_items = Mock()
    return client
  
@pytest.fixture
def mock_thread_data():
    return {
        "_id": ObjectId(mock_thread_id),
        "request": "Test request",
        "messages": [],
        "created_at": "2024-01-01T00:00:00.000Z",
        "updated_at": "2024-01-01T00:00:00.000Z"
    }

@pytest.fixture
def mock_thread_item_data():
    return {
        "_id": ObjectId(),
        "thread_id": ObjectId(mock_thread_id),
        "content": "Test content",
        "user_id": mock_user_id,
        "userType": "user",
        "block": {
            "document_id": str(ObjectId()),
            "document_type": "test"
        },
        "context_document_ids": [str(ObjectId())],
        "steps": [],
        "created_at": "2024-01-01T00:00:00.000Z"
    }

@pytest.mark.asyncio
class TestThreadService:
    @patch('services.thread_service.MongoClient')
    async def test_create_thread(self, mock_mongo_client, mock_client, mock_thread_data):
        # Arrange
        mock_mongo_client.return_value = mock_client
        mock_client.brade_dev.threads.insert_one.return_value.inserted_id = mock_thread_data["_id"]
        mock_client.brade_dev.threads.find_one.return_value = mock_thread_data
        
        # Act
        result = create_thread_service("Test request", mock_client)
        
        # Assert
        assert result["id"] == mock_thread_id
        mock_client.brade_dev.threads.insert_one.assert_called_once()
        mock_client.brade_dev.threads.find_one.assert_called_once()

    @patch('services.thread_service.MongoClient')
    async def test_get_threads(self, mock_mongo_client, mock_client, mock_thread_data):
        # Arrange
        mock_mongo_client.return_value = mock_client
        mock_client.brade_dev.threads.count_documents.return_value = 1
        mock_client.brade_dev.threads.find.return_value.skip.return_value.limit.return_value = [mock_thread_data]
        
        # Act
        result = get_threads_service(1, 20, mock_client)
        
        # Assert
        assert len(result["threads"]) == 1
        assert result["total"] == 1
        assert result["page"] == 1
        assert result["page_size"] == 20
        mock_client.brade_dev.threads.find.assert_called_once()

    @patch('services.thread_service.MongoClient')
    async def test_get_thread(self, mock_mongo_client, mock_client, mock_thread_data):
        # Arrange
        mock_mongo_client.return_value = mock_client
        mock_client.brade_dev.threads.find_one.return_value = mock_thread_data
        
        # Act
        result = get_thread_service(mock_thread_id, 1, 20, mock_client)
        
        # Assert
        assert result["id"] == mock_thread_id
        mock_client.brade_dev.threads.find_one.assert_called_once()

    @patch('services.thread_service.MongoClient')
    async def test_get_thread_not_found(self, mock_mongo_client, mock_client):
        # Arrange
        mock_mongo_client.return_value = mock_client
        mock_client.brade_dev.threads.find_one.return_value = None
        
        # Act
        result = get_thread_service(mock_thread_id, 1, 20, mock_client)
        
        # Assert
        assert result is None

    @patch('services.thread_service.MongoClient')
    async def test_add_thread_item(self, mock_mongo_client, mock_client, mock_thread_item_data):
        # Arrange
        mock_mongo_client.return_value = mock_client
        mock_client.brade_dev.thread_items.insert_one.return_value.inserted_id = mock_thread_item_data["_id"]
        mock_client.brade_dev.thread_items.find_one.return_value = mock_thread_item_data
        
        thread_item = ThreadItemModel(
            thread_id=mock_thread_id,
            content="Test content",
            user_id=mock_user_id,
            userType=UserType.user,
            block=BlockModel(
                document_id=str(ObjectId()),
                document_type="test"
            ),
            context_document_ids=[str(ObjectId())],
            steps=[]
        )
        
        # Act
        result = add_thread_item_service(
            thread_id=mock_thread_id,
            content=thread_item.content,
            user_id=mock_user_id,
            user_type=thread_item.userType,
            block=thread_item.block.model_dump(),
            context_document_ids=thread_item.context_document_ids,
            steps=thread_item.steps,
            client=mock_client
        )
        
        # Assert
        assert result["content"] == "Test content"
        assert result["thread_id"] == str(mock_thread_item_data["thread_id"])
        mock_client.brade_dev.thread_items.insert_one.assert_called_once()