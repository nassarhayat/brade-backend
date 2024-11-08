from pydantic import BaseModel
from enum import Enum
from typing import List, Optional
from .block import Block

class ThreadUserType(str, Enum):
    user = "user"
    assistant = "assistant"
    system = "system"

class ThreadItem(BaseModel):
  id: str
  content: str
  userType: ThreadUserType
  userId: Optional[str]
  block: Optional[Block]
  
class ThreadItemCreateRequest(BaseModel):
  content: str