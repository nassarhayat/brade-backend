from pymongo.mongo_client import MongoClient
from repositories.threads import add_thread_item_repo, get_thread_with_items_repo, get_threads_repo, create_thread_repo
from models.thread import ThreadItemModel, ThreadModel, ThreadItemUserType
from typing import Optional, Dict
from datetime import datetime
from bson.objectid import ObjectId
from schemas.thread import ThreadItemCreateRequest

def create_thread_service(user_request: str, client: MongoClient):
    generated_name = generate_thread_name(user_request)
    
    thread_data = {
        "id": str(ObjectId()),
        "name": generated_name,
        "created": datetime.utcnow(),
        "updated": datetime.utcnow(),
        "status": "active"
    }
    
    # Create thread model and save to database
    thread_model = ThreadModel(**thread_data)
    created_thread = create_thread_repo(thread_model, client)
    
    if not created_thread:
        return None
        
    return created_thread

def generate_thread_name(user_request: str) -> str:
    # Take first few words (up to 5) and add ellipsis if needed
    words = user_request.split()
    name = " ".join(words[:5])
    if len(words) > 5:
        name += "..."
    return name

def add_thread_item_service(thread_id: str, thread_item_data: ThreadItemCreateRequest, user_id: str, client: MongoClient):
    thread_item = ThreadItemModel(
        created=datetime.utcnow(),
        updated=datetime.utcnow(),
        thread_id=thread_id,
        content=thread_item_data.content,
        user_id=user_id,
        userType=ThreadItemUserType.user,
        block=thread_item_data.block if hasattr(thread_item_data, 'block') else None,
        context_document_ids=thread_item_data.contextDocumentIds,
        steps=thread_item_data.steps if hasattr(thread_item_data, 'steps') else []
    )
    
    return add_thread_item_repo(thread_id, thread_item, client)

def get_thread_service(thread_id: str, page: int = 1, page_size: int = 20, client: MongoClient = None) -> Optional[Dict]:
    thread = get_thread_with_items_repo(thread_id, page, page_size, client)
    print("Thread data from service:", thread)
    if not thread:
        return None
    
    # Format the items to match ThreadItem schema
    formatted_items = [{
        "id": item["id"],
        "content": item["content"],
        "userType": item["userType"],
        "userId": item.get("user_id"),
        "blockDocumentId": item.get("block_document_id"),
        "threadId": str(thread_id),
        "contextDocumentIds": item.get("context_document_ids", []),
        "steps": [{
            "step_id": step.get("step_id"),
            "tool": step.get("tool"),
            "input": step.get("input"),
            "timestamp": step.get("timestamp")
        } for step in item.get("steps", [])]
    } for item in thread["items"]]
        
    # Format the response to match ThreadResponse schema
    return {
        "id": thread["id"],
        "name": thread["name"],
        "created": thread["created"],
        "updated": thread["updated"],
        "items": formatted_items,
        "pagination": thread["pagination"]  # Use pagination from repo
    }

def get_threads_service(page: int = 1, page_size: int = 20, client: MongoClient = None) -> Optional[Dict]:
    threads_data = get_threads_repo(page, page_size, client)
    if not threads_data:
        return None
        
    # Format each thread to match ThreadResponse schema
    formatted_threads = []
    for thread in threads_data["threads"]:
        formatted_thread = {
            "id": thread["id"],
            "name": thread["name"],
            "created": thread["created"],
            "updated": thread["updated"],
            "items": thread.get("items", []),
            "pagination": {
                "total": threads_data["total"],  # Use the total from repo
                "page": page,
                "page_size": page_size,
                "total_pages": (threads_data["total"] + page_size - 1) // page_size
            }
        }
        formatted_threads.append(formatted_thread)
    
    return {
        "threads": formatted_threads,
        "pagination": {
            "total": threads_data["total"],
            "page": page,
            "page_size": page_size,
            "total_pages": (threads_data["total"] + page_size - 1) // page_size
        }
    }

def get_thread_items(thread_id: str, client: MongoClient):
    """Get all thread items for a thread"""
    items = client.brade_dev.thread_items.find(
        {"thread_id": ObjectId(thread_id)}
    ).sort("created", -1).limit(20)
    
    # Format items to exactly match ThreadItem schema
    return [{
        "id": str(item["_id"]),
        "content": item["content"],
        "userType": item["userType"],
        "userId": item.get("user_id"),
        "blockDocumentId": item.get("block_document_id"),
        "threadId": str(item.get("thread_id")),
        "contextDocumentIds": item.get("context_document_ids", []),
        "steps": item.get("steps", [])
    } for item in items][::-1] 