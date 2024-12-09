from typing import Dict, List, Optional
from datetime import datetime
from pymongo.mongo_client import MongoClient

def update_document_index_repo(document_id: str, index_data: Dict, client: MongoClient) -> Dict:
    """Update or create document index"""
    try:
        client.brade.document_indices.update_one(
            {"id": document_id},
            {"$set": {
                **index_data,
                "updated_at": datetime.utcnow()
            }},
            upsert=True
        )
        
        updated_doc = client.brade.document_indices.find_one({"id": document_id})
        if not updated_doc:
            raise Exception(f"Failed to retrieve document index after update for id: {document_id}")
            
        updated_doc["id"] = str(updated_doc.pop("_id"))
        return updated_doc
    except Exception as e:
        print(f"Error in update_document_index_repo: {str(e)}")
        raise

def search_document_indices_repo(
    query: str,
    document_type: Optional[str] = None,
    tags: Optional[List[str]] = None,
    limit: int = 50,
    skip: int = 0,
    client: MongoClient = None
) -> List[Dict]:
    """Search document indices"""
    try:
        search_query = {"$text": {"$search": query}} if query else {}
        if document_type:
            search_query["document_type"] = document_type
        if tags:
            search_query["tags"] = {"$all": tags}

        cursor = client.brade.document_indices.find(
            search_query,
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]).skip(skip).limit(limit)

        documents = list(cursor)  # Convert cursor to list immediately
        for doc in documents:
            doc["id"] = str(doc.pop("_id"))
        
        return documents
    except Exception as e:
        print(f"Error in search_document_indices_repo: {str(e)}")
        raise

def get_documents_repo(
    document_type: Optional[str] = None,
    tags: Optional[List[str]] = None,
    limit: int = 50,
    skip: int = 0,
    client: MongoClient = None
) -> List[Dict]:
    """Get documents with optional filtering"""
    try:
        query = {}
        if document_type:
            query["document_type"] = document_type
        if tags:
            query["tags"] = {"$all": tags}

        cursor = client.brade.document_indices.find(query).skip(skip).limit(limit)
        
        documents = list(cursor)  # Convert cursor to list immediately
        for doc in documents:
            doc["id"] = str(doc.pop("_id"))
            
        return documents
    except Exception as e:
        print(f"Error in get_documents_repo: {str(e)}")
        raise
