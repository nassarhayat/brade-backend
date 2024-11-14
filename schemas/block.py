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
  id: str = Field(alias="_id")
  blockType: str
  data: Any
  layout: Optional[LayoutItem] = None
  
  @validator("id", pre=True)
  def convert_objectid_to_str(cls, value):
    if isinstance(value, ObjectId):
        return str(value)
    return value

class BlockCreateRequest(BaseModel):
  blockType: str
  data: Any