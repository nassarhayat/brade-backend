from pydantic import BaseModel, Field

class Block(BaseModel):
  id: str = Field()
  documentId: str
  documentType: str

class BlockCreateRequest(BaseModel):
  id: str
  
class BlockAddResponse(BaseModel):
  blockId: str