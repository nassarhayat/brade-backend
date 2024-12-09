import pytest
from datetime import datetime, UTC
from models.document_index import DocumentIndex
from repositories.documents_index import (
    create_document_index_repo,
    search_document_indices_repo,
    upsert_document_index_repo,
)
from unittest.mock import Mock, patch

@pytest.fixture
def mock_client():
    return Mock()

@pytest.fixture
def sample_document():
    return {
        "document_id": "test-doc-123",
        "title": "Test Document",
        "content": "This is a test document content",
        "document_type": "note",
        "tags": ["test", "sample"]
    }

@pytest.fixture
def sample_document_with_dates(sample_document):
    return {
        **sample_document,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "_id": "mock_object_id"
    }

async def test_create_document_index(mock_client, sample_document):
    # Arrange
    doc_index = DocumentIndex(**sample_document)
    mock_client.brade_dev.document_indices.insert_one.return_value.inserted_id = "mock_id"
    mock_client.brade_dev.document_indices.find_one.return_value = {
        **sample_document,
        "_id": "mock_id",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    }
    
    # Act
    result = create_document_index_repo(doc_index, mock_client)
    
    # Assert
    assert result["document_id"] == sample_document["document_id"]
    assert result["title"] == sample_document["title"]
    mock_client.brade_dev.document_indices.insert_one.assert_called_once()

async def test_upsert_document_index(mock_client, sample_document, sample_document_with_dates):
    # Arrange
    mock_client.brade_dev.document_indices.update_one.return_value.modified_count = 1
    mock_client.brade_dev.document_indices.find_one.return_value = sample_document_with_dates
    
    # Act
    result = upsert_document_index_repo(
        sample_document["document_id"],
        sample_document,
        mock_client
    )
    
    # Assert
    assert result["document_id"] == sample_document["document_id"]
    assert result["title"] == sample_document["title"]
    mock_client.brade_dev.document_indices.update_one.assert_called_once()

async def test_search_document_indices(mock_client, sample_document_with_dates):
    # Arrange
    mock_find = Mock()
    mock_find.sort = Mock(return_value=[sample_document_with_dates])
    mock_client.brade_dev.document_indices.find.return_value = mock_find
    
    search_query = "test"
    
    # Act
    results = search_document_indices_repo(search_query, mock_client)
    
    # Assert
    assert len(results) == 1
    assert results[0]["document_id"] == sample_document_with_dates["document_id"]
    mock_client.brade_dev.document_indices.find.assert_called_once_with(
        {"$text": {"$search": search_query}},
        {"score": {"$meta": "textScore"}}
    )
    mock_find.sort.assert_called_once_with([("score", {"$meta": "textScore"})])