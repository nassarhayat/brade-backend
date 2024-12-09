from datetime import datetime
from models.document_index import DocumentIndex

def test_document_index_creation():
    # Test the model itself
    doc = DocumentIndex(
        document_id="test-123",
        title="Test Doc",
        content="Content",
        document_type="note"
    )
    
    assert doc.document_id == "test-123"
    assert doc.title == "Test Doc"
    assert isinstance(doc.created_at, datetime)
    assert isinstance(doc.updated_at, datetime)
    assert doc.tags == [] 