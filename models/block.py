from pydantic import BaseModel, Field
from enum import Enum
from typing import Any
from bson import ObjectId

class BlockType(str, Enum):
    number = "number"
    chart = "chart"
    table = "table"

class BlockModel(BaseModel):
  id: str = Field(default_factory=lambda: ObjectId(), alias="_id")
  blockType: BlockType
  data: Any