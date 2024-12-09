from pymongo.mongo_client import MongoClient
from models.thread import ThreadModel, ThreadItemModel
from datetime import datetime
from bson import ObjectId
from typing import Optional, Dict

def create_thread_repo(thread: ThreadModel, client: MongoClient = None) -> Dict:
    if client is None:
        client = MongoClient()
    
    thread_dict = thread.model_dump()
    # Convert string ID to ObjectId for MongoDB
    thread_dict["_id"] = ObjectId(thread_dict["id"])
    del thread_dict["id"]  # Remove string ID as we're using _id
    
    result = client.brade_dev.threads.insert_one(thread_dict)
    created_thread = client.brade_dev.threads.find_one({"_id": result.inserted_id})
    
    return {
        "id": str(created_thread["_id"]),
        "name": created_thread["name"],
        "created": created_thread["created"],
        "updated": created_thread["updated"],
        "status": created_thread["status"]
    }

def get_thread_with_items_repo(thread_id: str, page: int, page_size: int, client: MongoClient = None) -> Optional[Dict]:
    if client is None:
        client = MongoClient()
    
    thread = client.brade_dev.threads.find_one({"_id": ObjectId(thread_id)})
    
    if not thread:
        return None
    
    # Get total count of items for this thread
    total_items = client.brade_dev.thread_items.count_documents({"thread_id": ObjectId(thread_id)})
    total_pages = (total_items + page_size - 1) // page_size
    
    # Calculate skip based on page number directly
    skip = (page - 1) * page_size
    limit = page_size
    
    # Fetch thread items with pagination - newest first
    items_cursor = client.brade_dev.thread_items.find(
        {"thread_id": ObjectId(thread_id)}
    ).sort("created", -1).skip(skip).limit(limit)
    
    items_list = list(items_cursor)
    
    items = [{
        "id": str(item["_id"]),
        "thread_id": str(item["thread_id"]),
        "content": item.get("content", ""),
        "user_id": item.get("user_id", ""),
        "userType": item.get("userType", "user"),
        "block_document_id": item.get("block_document_id"),
        "context_document_ids": item.get("context_document_ids", []),
        "steps": item.get("steps", []),
        "created": item.get("created", datetime.utcnow())
    } for item in items_list]
    
    result = {
        "id": str(thread["_id"]),
        "name": thread.get("name", "Untitled Thread"),
        "created": thread.get("created", datetime.utcnow()),
        "updated": thread.get("updated", datetime.utcnow()),
        "status": thread.get("status", "active"),
        "items": items,
        "pagination": {
            "total": total_items,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    }
    return result

def get_threads_repo(page: int, page_size: int, client: MongoClient = None) -> Dict:
    if client is None:
        client = MongoClient()
        
    skip = (page - 1) * page_size
    total = client.brade_dev.threads.count_documents({})
    
    cursor = client.brade_dev.threads.find({}).sort("created", -1).skip(skip).limit(page_size)
    threads = []
    
    for thread in cursor:
        threads.append({
            "id": str(thread["_id"]),
            "name": thread.get("name", "Untitled Thread"),
            "created": thread.get("created", datetime.utcnow()),
            "updated": thread.get("updated", datetime.utcnow()),
            "status": thread.get("status", "active")
        })
    
    return {
        "threads": threads,
        "total": total,
        "page": page,
        "page_size": page_size
    }

def add_thread_item_repo(thread_id: str, thread_item: ThreadItemModel, client: MongoClient = None) -> Optional[Dict]:
    if client is None:
        client = MongoClient()
    
    thread_item_doc = thread_item.model_dump()
    # print("THREAD ITEM DOC", thread_item_doc)
    thread_item_doc["thread_id"] = ObjectId(thread_id)
    print("THREAD ITEM DOC", thread_item_doc)
    result = client.brade_dev.thread_items.insert_one(thread_item_doc)
    created_item = client.brade_dev.thread_items.find_one({"_id": result.inserted_id})
    
    return {
        "id": str(created_item["_id"]),
        "thread_id": str(created_item["thread_id"]),
        "content": created_item["content"],
        "user_id": created_item["user_id"],
        "userType": created_item["userType"],
        "block_document_id": created_item["block_document_id"],
        "context_document_ids": created_item["context_document_ids"],
        "steps": created_item["steps"],
        "created": created_item["created"]
    } 
    
def get_thread_repo(thread_id: str, client: MongoClient = None) -> Optional[Dict]:
    if client is None:
        client = MongoClient()
    
    return client.brade_dev.threads.find_one({"_id": ObjectId(thread_id)})