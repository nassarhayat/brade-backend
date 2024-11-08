from pydantic import BaseModel, Field, validator
from enum import Enum
from typing import List, Optional
from .block import Block
from bson import ObjectId

class ThreadUserType(str, Enum):
    user = "user"
    assistant = "assistant"
    system = "system"

class ThreadItem(BaseModel):
  id: str = Field(alias="_id")
  content: str
  userType: ThreadUserType
  userId: Optional[str]
  block: Optional[Block]
  
  @validator("id", pre=True)
  def convert_objectid_to_str(cls, value):
    if isinstance(value, ObjectId):
        return str(value)
    return value

  
class ThreadItemCreateRequest(BaseModel):
  content: str