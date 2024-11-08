from pydantic import BaseModel, EmailStr

class User(BaseModel):
  name: str
  # email: EmailStr
  avatarUrl: str