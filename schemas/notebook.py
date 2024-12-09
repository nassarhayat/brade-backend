from pydantic import BaseModel
from typing import Optional, List
from .block import Block

class NotebooksResponse(BaseModel):
    id: str
    title: str
    
class NotebookCreateRequest(BaseModel):
    userRequest: str
    
class NotebookUpdateRequest(BaseModel):
    title: Optional[str] = None

class NotebookResponse(BaseModel):
    id: str
    title: str
    blocks: Optional[List[Block]] = None

class Notebook(BaseModel):
    id: str
    title: str
    blocks: Optional[List[Block]] = None