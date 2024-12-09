from pydantic import BaseModel, Field
from typing import Optional

class DataConnectorModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    type: str
    db_host: Optional[str]
    db_name: Optional[str]
    db_user: Optional[str]
    db_password: Optional[str]
    db_port: Optional[int]
    user_id: str
