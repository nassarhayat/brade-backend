from typing import Dict, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

class DocumentBase(BaseModel):
    title: str
    content: Dict
    metadata: Optional[Dict] = Field(default_factory=dict)

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[Dict] = None
    metadata: Optional[Dict] = None

class DocumentResponse(DocumentBase):
    id: str
    created_at: datetime
    updated_at: datetime
    version: int = 1

class DocumentSearchQuery(BaseModel):
    query: str
    document_type: Optional[str] = None
    tags: Optional[List[str]] = None
    limit: Optional[int] = Field(default=10, ge=1, le=100)
    skip: Optional[int] = Field(default=0, ge=0)

class DocumentSearchResponse(BaseModel):
    total: int
    documents: List[DocumentResponse]