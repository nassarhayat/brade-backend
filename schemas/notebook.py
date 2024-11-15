from pydantic import BaseModel
from typing import Optional, List
from .thread import ThreadItem
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
    thread_items: List[ThreadItem] = []

class Notebook(BaseModel):
    id: str
    title: str
    thread_items: Optional[List[ThreadItem]] = None
    blocks: Optional[List[Block]] = None