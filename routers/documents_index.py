from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, List, Optional
from pymongo.mongo_client import MongoClient
from services.document_index_service import update_document_index, search_documents, get_documents
from schemas.documents import DocumentSearchQuery, DocumentSearchResponse
from db import get_mongo_client
from pydantic import BaseModel

class DocumentIndexUpdate(BaseModel):
    title: str
    content: str
    document_type: str
    tags: List[str] = []
    author: Optional[str] = None
    source_url: Optional[str] = None
    summary: Optional[str] = None

router = APIRouter()

@router.post("/documents_index/{document_id}")
async def update_document_index_route(
    document_id: str, 
    document_data: DocumentIndexUpdate,
    client: MongoClient = Depends(get_mongo_client)
):
    """Update document indices when document is created or updated"""
    try:
        await update_document_index(document_id, document_data.model_dump(), client)
        return {"status": "success", "message": "Document index updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update document index: {str(e)}")

@router.get("/documents_index", response_model=List[DocumentSearchResponse])
async def get_documents_index_route_route(
    type: Optional[str] = Query(None),
    tags: Optional[List[str]] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
    client: MongoClient = Depends(get_mongo_client)
):
    """Get all document indices with optional filtering"""
    try:
        documents = get_documents(
            document_type=type,
            tags=tags,
            limit=limit,
            skip=skip,
            client=client
        )
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents_index/search", response_model=DocumentSearchResponse)
async def search_documents_index_route(
    search_query: DocumentSearchQuery,
    client: MongoClient = Depends(get_mongo_client)
):
    """Search document indices using MongoDB text search"""
    try:
        results = await search_documents(
            query=search_query.query,
            document_type=search_query.document_type,
            tags=search_query.tags,
            limit=search_query.limit,
            skip=search_query.skip,
            client=client
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 