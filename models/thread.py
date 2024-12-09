from pydantic import BaseModel, Field
from typing import Optional, List, Any
from enum import Enum
from datetime import datetime
from bson import ObjectId

class ThreadItemUserType(str, Enum):
    user = "user"
    assistant = "assistant"
    system = "system"

# class BlockModel(BaseModel):
#     id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
#     document_id: str
#     document_type: str

class ThreadItemModel(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    created: datetime = Field(default_factory=datetime.utcnow)
    updated: datetime = Field(default_factory=datetime.utcnow)
    thread_id: str
    user_id: Optional[str] = None
    content: str
    userType: ThreadItemUserType
    block_document_id: Optional[str] = None
    context_document_ids: List[str] = Field(default_factory=list)
    steps: List[Any] = Field(default_factory=list)

class ThreadModel(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    name: str
    created: datetime = Field(default_factory=datetime.utcnow)
    updated: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="active")
  
