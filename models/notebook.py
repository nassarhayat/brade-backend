from pydantic import BaseModel, Field
from typing import List
from bson import ObjectId
from .thread import ThreadItemModel

class NotebookModel(BaseModel):
  id: str = Field(default_factory=lambda: ObjectId(), alias="_id")
  title: str
  thread: List[ThreadItemModel] = []