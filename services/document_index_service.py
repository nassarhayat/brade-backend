from typing import Dict, List, Optional
from datetime import datetime
from pymongo.mongo_client import MongoClient
from models.document_index import DocumentIndex
from repositories.documents_index import (
    update_document_index_repo,
    search_document_indices_repo,
    get_documents_repo
)

def update_document_index(document_id: str, content: Dict, client: MongoClient) -> DocumentIndex:
    """Update document index with document information"""
    try:
        # Create DocumentIndex instance with the provided content
        index_data = DocumentIndex(
            id=document_id,
            title=content.get("title", "Untitled"),
            content=content.get("content", ""),
            document_type=content.get("type", "document"),
            tags=content.get("tags", []),
            author=content.get("author"),
            updated_at=datetime.utcnow(),
            summary=content.get("summary"),
            parent_id=content.get("parent_id"),
            related_ids=content.get("related_ids", []),
            source_url=content.get("source_url"),
            is_archived=content.get("is_archived", False)
        )

        # Update document index using repository
        updated_index = update_document_index_repo(document_id, index_data.model_dump(), client)
        print(f"Successfully updated index for document {document_id}")
        return DocumentIndex(**updated_index)
    except Exception as e:
        print(f"Error updating document index: {str(e)}")
        raise

def search_documents(
    query: str,
    document_type: Optional[str] = None,
    tags: Optional[List[str]] = None,
    limit: int = 50,
    skip: int = 0,
    client: MongoClient = None
) -> Dict:
    """Search documents using MongoDB text search"""
    try:
        results = search_document_indices_repo(
            query=query,
            document_type=document_type,
            tags=tags,
            limit=limit,
            skip=skip,
            client=client
        )
        
        return {
            "results": [DocumentIndex(**doc) for doc in results],
            "total": len(results),
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        print(f"Error searching documents: {str(e)}")
        raise

def get_documents(
    document_type: Optional[str] = None,
    tags: Optional[List[str]] = None,
    limit: int = 50,
    skip: int = 0,
    client: MongoClient = None
) -> List[DocumentIndex]:
    """Get documents with optional filtering"""
    try:
        documents = get_documents_repo(
            document_type=document_type,
            tags=tags,
            limit=limit,
            skip=skip,
            client=client
        )
        return [DocumentIndex(**doc) for doc in documents]
    except Exception as e:
        print(f"Error getting documents: {str(e)}")
        raise 