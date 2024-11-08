from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from .block import BlockModel
from bson import ObjectId

class UserType(str, Enum):
    user = "user"
    assistant = "assistant"
    system = "system"

class ThreadItemModel(BaseModel):
  id: str = Field(default_factory=lambda: ObjectId(), alias="_id")
  content: str
  userType: UserType
  userId: Optional[str] = None
  block: Optional[BlockModel] = None
  
  
