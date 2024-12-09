import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_documents_index():
    response = client.get("/api/documents-index")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_update_document_index():
    document_id = "test_doc_id"
    content = {"text": "Test content"}
    response = client.post(f"/api/documents-index/{document_id}", json=content)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_search_documents_index():
    search_query = {
        "query": "test",
        "document_type": None,
        "tags": None,
        "limit": 10,
        "skip": 0
    }
    response = client.post("/api/documents-index/search", json=search_query)
    assert response.status_code == 200 