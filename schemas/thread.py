from pydantic import BaseModel, Field, validator
from enum import Enum
from typing import List, Optional, Any
from .block import Block
from datetime import datetime

class ThreadItemUserType(str, Enum):
    user = "user"
    assistant = "assistant"
    system = "system"

class ThreadItem(BaseModel):
    id: str
    content: str
    userType: ThreadItemUserType
    userId: Optional[str] = None
    blockDocumentId: Optional[str] = None
    threadId: Optional[str] = None
    contextDocumentIds: Optional[List[str]] = Field(default_factory=list, alias="contextDocumentIds")
    steps: Optional[List[Any]] = Field(default_factory=list)
  
class ThreadItemCreateRequest(BaseModel):
    content: str
    userType: ThreadItemUserType = Field(default=ThreadItemUserType.user)
    contextDocumentIds: List[str] = Field(default_factory=list)
    
class ThreadCreateRequest(BaseModel):
    userRequest: str = Field(description="Initial user request to start the thread")

class PaginationResponse(BaseModel):
    total: int
    page: int = Field(default=1)
    page_size: int = Field(default=20, alias="page_size")
    total_pages: int = Field(default=1, alias="total_pages")

class ThreadResponse(BaseModel):
    id: str
    name: str = Field(description="Name of the thread")
    created: datetime = Field(default_factory=datetime.utcnow)
    updated: datetime = Field(default_factory=datetime.utcnow)
    items: List[ThreadItem] = Field(default_factory=list)
    pagination: PaginationResponse

class ThreadsResponse(BaseModel):
    threads: List[ThreadResponse] = Field(default_factory=list)
    pagination: PaginationResponse
