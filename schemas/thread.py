from pydantic import BaseModel, Field, validator
from enum import Enum
from typing import List, Optional
from .block import Block

class ThreadUserType(str, Enum):
    user = "user"
    assistant = "assistant"
    system = "system"

class ThreadItem(BaseModel):
  id: str = Field()
  content: str
  userType: ThreadUserType
  userId: Optional[str] = None
  block: Optional[Block] = None

  
class ThreadItemCreateRequest(BaseModel):
  content: str