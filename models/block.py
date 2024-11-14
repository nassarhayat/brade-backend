from pydantic import BaseModel, Field
from enum import Enum
from typing import Any, Optional, List
from bson import ObjectId

class BlockType(str, Enum):
    number = "number"
    chart = "chart"
    table = "table"
    stacked_chart = "stacked_chart"
    line_chart = "line_chart"
    
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

class BlockModel(BaseModel):
  id: str = Field(default_factory=lambda: ObjectId(), alias="_id")
  blockType: BlockType
  data: Any
  layout: Optional[LayoutItem] = None