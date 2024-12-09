import pytest
from services.document_service import (
    get_document,
    update_document,
    update_document_indices,
    search_documents
)

@pytest.mark.integration
async def test_complete_document_flow(mongo_client):
    # Create document
    doc_data = {
        "title": "Integration Test Doc",
        "content": "This is an integration test",
        "document_type": "note",
        "tags": ["test", "integration"]
    }
    
    # Create and index document
    created_doc = await update_document(None, doc_data)
    assert isinstance(created_doc, dict), "Expected document object, got boolean"
    assert "document_id" in created_doc, "Created document missing document_id"
    
    # Index the document
    await update_document_indices(
        created_doc["document_id"],
        created_doc,
        mongo_client
    )
    
    # Update document
    update_data = {"title": "Updated Integration Test"}
    updated = await update_document(created_doc["document_id"], update_data)
    assert updated is True
    
    # Get updated document
    updated_doc = await get_document(created_doc["document_id"])
    assert updated_doc is not None
    assert updated_doc["title"] == "Updated Integration Test"
    
    # Update index with full document
    await update_document_indices(
        created_doc["document_id"],
        updated_doc,
        mongo_client
    )
    
    # Search document
    search_results = await search_documents("integration", client=mongo_client)
    assert search_results["total"] > 0
    assert any(doc["document_id"] == created_doc["document_id"] 
              for doc in search_results["documents"])
    
    # Cleanup
    await update_document(created_doc["document_id"], None)
    await update_document_indices(
        created_doc["document_id"],
        None,
        mongo_client
    )