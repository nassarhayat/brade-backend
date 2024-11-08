from pydantic import BaseModel, Field, validator
from bson import ObjectId
from typing import Any

class Block(BaseModel):
  id: str = Field(alias="_id")
  blockType: str
  data: Any
  
  @validator("id", pre=True)
  def convert_objectid_to_str(cls, value):
    if isinstance(value, ObjectId):
        return str(value)
    return value
