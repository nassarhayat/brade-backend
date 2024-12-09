import pytest
from fastapi.testclient import TestClient
from main import app
from bson import ObjectId
from datetime import datetime

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_teardown(mongo_client):
    # Setup: Clear test collections before each test
    mongo_client.brade_test.threads.delete_many({})
    mongo_client.brade_test.thread_items.delete_many({})
    yield
    # Teardown: Clear test collections after each test
    mongo_client.brade_test.threads.delete_many({})
    mongo_client.brade_test.thread_items.delete_many({})

def test_create_and_get_thread(mongo_client):
    # Create a thread
    create_response = client.post("/threads", json={
        "userRequest": "Test integration thread"
    })
    assert create_response.status_code == 200, f"Create response: {create_response.text}"
    
    thread_data = create_response.json()
    print(f"Thread data: {thread_data}")
    
    # Check if either 'request' or 'userRequest' exists
    request_text = thread_data.get("request") or thread_data.get("userRequest")
    assert request_text == "Test integration thread"
    assert "id" in thread_data
    assert "created_at" in thread_data
    assert "updated_at" in thread_data
    
    # Get the created thread
    thread_id = thread_data["id"]
    get_response = client.get(f"/threads/{thread_id}")
    assert get_response.status_code == 200, f"Get response: {get_response.text}"
    
    retrieved_thread = get_response.json()
    print(f"Retrieved thread: {retrieved_thread}")
    assert retrieved_thread["id"] == thread_id
    request_text = retrieved_thread.get("request") or retrieved_thread.get("userRequest")
    assert request_text == "Test integration thread"

def test_get_threads_pagination(mongo_client):
    # Create multiple threads
    threads = []
    for i in range(5):
        response = client.post("/threads", json={
            "userRequest": f"Test thread {i}"
        })
        threads.append(response.json())
    
    # Test first page
    response = client.get("/threads?page=1&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["threads"]) == 2
    assert data["page"] == 1
    assert data["page_size"] == 2
    
    # Test second page
    response = client.get("/threads?page=2&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["threads"]) == 2

def test_add_thread_item(mongo_client):
    # Create a thread first
    thread_response = client.post("/threads", json={
        "userRequest": "Thread with items"
    })
    assert thread_response.status_code == 200
    thread_id = thread_response.json()["id"]
    
    # Add an item to the thread
    item_response = client.post(f"/threads/{thread_id}/items", json={
        "content": "Test thread item",
        "userType": "user",
        "block": {
            "document_id": str(ObjectId()),
            "document_type": "test"
        },
        "context_document_ids": [str(ObjectId())],
        "steps": []
    })
    assert item_response.status_code == 200
    item_data = item_response.json()
    assert item_data["content"] == "Test thread item"
    assert item_data["thread_id"] == thread_id

def test_complete_thread_flow(mongo_client):
    # 1. Create a thread
    thread_response = client.post("/threads", json={
        "userRequest": "Complete flow test"
    })
    assert thread_response.status_code == 200
    thread_id = thread_response.json()["id"]
    
    # 2. Add multiple items
    items = []
    for i in range(3):
        item_response = client.post(f"/threads/{thread_id}/items", json={
            "content": f"Item {i}",
            "userType": "user",
            "block": {
                "document_id": str(ObjectId()),
                "document_type": "test"
            },
            "context_document_ids": [str(ObjectId())],
            "steps": []
        })
        assert item_response.status_code == 200
        items.append(item_response.json())
    
    # 3. Get thread with items
    thread_response = client.get(f"/threads/{thread_id}")
    assert thread_response.status_code == 200
    thread_data = thread_response.json()
    assert len(thread_data["messages"]) == 3

def test_error_cases(mongo_client):
    # Test non-existent thread with valid ObjectId
    non_existent_id = str(ObjectId())
    response = client.get(f"/threads/{non_existent_id}")
    assert response.status_code == 404
    
    # Test invalid pagination
    response = client.get("/threads?page=0&page_size=0")
    assert response.status_code == 422
    
    # Test invalid thread item
    thread_response = client.post("/threads", json={
        "userRequest": "Error test"
    })
    thread_id = thread_response.json()["id"]
    
    invalid_item_response = client.post(f"/threads/{thread_id}/items", json={
        "content": "",  # Empty content
        "userType": "invalid_type"  # Invalid user type
    })
    assert invalid_item_response.status_code == 422