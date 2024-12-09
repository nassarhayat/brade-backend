import pytest
from unittest.mock import Mock
from bson import ObjectId
from repositories.threads import (
    create_thread_repo,
    get_thread_with_items_repo,
    get_threads_repo,
    add_thread_item_repo
)
from models.thread import ThreadModel, ThreadItemModel

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
def mock_thread_doc():
    return {
        "_id": ObjectId(mock_thread_id),
        "request": "Test request",
        "messages": [],
        "created_at": "2024-01-01T00:00:00.000Z",
        "updated_at": "2024-01-01T00:00:00.000Z"
    }

@pytest.fixture
def mock_thread_item_doc():
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

class TestThreadRepository:
    def test_create_thread(self, mock_client, mock_thread_doc):
        # Arrange
        mock_client.brade_dev.threads.insert_one.return_value.inserted_id = mock_thread_doc["_id"]
        mock_client.brade_dev.threads.find_one.return_value = mock_thread_doc
        thread = ThreadModel(userRequest="Test request")

        # Act
        result = create_thread_repo(thread, mock_client)

        # Assert
        assert result["id"] == str(mock_thread_doc["_id"])
        assert result["request"] == mock_thread_doc["request"]
        mock_client.brade_dev.threads.insert_one.assert_called_once()
        mock_client.brade_dev.threads.find_one.assert_called_once_with({"_id": mock_thread_doc["_id"]})

    def test_get_thread_with_items(self, mock_client, mock_thread_doc):
        # Arrange
        mock_client.brade_dev.threads.find_one.return_value = mock_thread_doc

        # Act
        result = get_thread_with_items_repo(mock_thread_id, 1, 20, mock_client)

        # Assert
        assert result["id"] == str(mock_thread_doc["_id"])
        assert result["request"] == mock_thread_doc["request"]
        mock_client.brade_dev.threads.find_one.assert_called_once_with({"_id": ObjectId(mock_thread_id)})

    def test_get_thread_not_found(self, mock_client):
        # Arrange
        mock_client.brade_dev.threads.find_one.return_value = None

        # Act
        result = get_thread_with_items_repo(mock_thread_id, 1, 20, mock_client)

        # Assert
        assert result is None
        mock_client.brade_dev.threads.find_one.assert_called_once_with({"_id": ObjectId(mock_thread_id)})

    def test_get_threads(self, mock_client, mock_thread_doc):
        # Arrange
        mock_client.brade_dev.threads.count_documents.return_value = 1
        mock_client.brade_dev.threads.find.return_value.skip.return_value.limit.return_value = [mock_thread_doc]

        # Act
        result = get_threads_repo(1, 20, mock_client)

        # Assert
        assert len(result["threads"]) == 1
        assert result["total"] == 1
        assert result["page"] == 1
        assert result["page_size"] == 20
        mock_client.brade_dev.threads.count_documents.assert_called_once_with({})
        mock_client.brade_dev.threads.find.assert_called_once()

    def test_add_thread_item(self, mock_client, mock_thread_item_doc):
        # Arrange
        mock_client.brade_dev.thread_items.insert_one.return_value.inserted_id = mock_thread_item_doc["_id"]
        mock_client.brade_dev.thread_items.find_one.return_value = mock_thread_item_doc
        
        thread_item = ThreadItemModel(
            thread_id=mock_thread_id,
            content="Test content",
            user_id=mock_user_id,
            userType="user",
            block={
                "document_id": str(ObjectId()),
                "document_type": "test"
            },
            context_document_ids=[str(ObjectId())],
            steps=[]
        )

        # Act
        result = add_thread_item_repo(mock_thread_id, thread_item, mock_client)

        # Assert
        assert result["id"] == str(mock_thread_item_doc["_id"])
        assert result["content"] == mock_thread_item_doc["content"]
        assert result["thread_id"] == str(mock_thread_item_doc["thread_id"])
        mock_client.brade_dev.thread_items.insert_one.assert_called_once()
        mock_client.brade_dev.thread_items.find_one.assert_called_once_with({"_id": mock_thread_item_doc["_id"]}) 