from pydantic import BaseModel, Field, validator
from bson import ObjectId
from typing import Any, Optional, List

class LayoutItem(BaseModel):
  i: str
  x: int
  y: int
  w: int
  h: int
  minW: Optional[int] = 0
  minH: Optional[int] = 0
  maxW: Optional[int] = None
  maxH: Optional[int] = None
  static: Optional[bool] = False
  isDraggable: Optional[bool] = True
  isResizable: Optional[bool] = True
  resizeHandles: Optional[List[str]] = ["se"]
  isBounded: Optional[bool] = False

class Block(BaseModel):
  id: str = Field()
  blockType: str
  data: Any
  layout: Optional[LayoutItem] = None

class BlockCreateRequest(BaseModel):
  id: str
  
class BlockAddResponse(BaseModel):
  notebookId: str
  blockId: str
  layout: LayoutItem