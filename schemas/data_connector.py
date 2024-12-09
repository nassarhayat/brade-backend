from pydantic import BaseModel, Field
from typing import Optional

class DataConnectorBase(BaseModel):
    type: str
    db_host: Optional[str]
    db_name: Optional[str]
    db_user: Optional[str]
    db_password: Optional[str]
    db_port: Optional[int]
    user_id: Optional[str] = None

class DataConnectorCreate(DataConnectorBase):
    type: str

class DataConnectorResponse(BaseModel):
    id: str
    type: str
    db_host: str
    db_name: str
    db_user: str
    db_port: int
    user_id: str