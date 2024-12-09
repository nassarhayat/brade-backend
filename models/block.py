from pydantic import BaseModel, Field
from enum import Enum
from typing import Any, Optional
from bson import ObjectId
from datetime import datetime

class BlockType(Enum):
    text = "text"
    code = "code"
    table = "table"
    spreadsheet = "spreadsheet"
    line_chart = "line-chart"
    bar_chart = "bar-chart"

class BlockModel(BaseModel):
  id: str = Field(default_factory=lambda: str(ObjectId()))
  blockType: BlockType
  data: Any
  threadId: Optional[str] = None
  notebookId: Optional[str] = None
  created: datetime = Field(default_factory=datetime.utcnow)
  updated: datetime = Field(default_factory=datetime.utcnow)