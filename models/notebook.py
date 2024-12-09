from pydantic import BaseModel, Field
from bson import ObjectId

class NotebookModel(BaseModel):
    id: str = Field(default_factory=lambda: ObjectId(), alias="_id")
    title: str