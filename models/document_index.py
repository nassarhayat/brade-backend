from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class DocumentIndex(BaseModel):
    """
    Model representing the searchable index of a document
    """
    id: str = Field(..., description="Unique identifier matching the source document")
    title: str = Field(..., description="Document title for quick identification")
    content: str = Field(..., description="Processed/searchable content of the document")
    document_type: str = Field(..., description="Type of document (e.g., 'note', 'pdf', 'webpage')")
    tags: List[str] = Field(default=[], description="List of tags for categorization")
    
    # Metadata fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    author: Optional[str] = Field(None, description="Document author or creator")
    source_url: Optional[str] = Field(None, description="Original source URL if applicable")
    
    # Summary and semantic fields
    summary: Optional[str] = Field(None, description="AI-generated summary of the content")
    embedding: Optional[List[float]] = Field(None, description="Vector embedding for semantic search")
    
    # Reference fields
    parent_id: Optional[str] = Field(None, description="ID of parent document if nested")
    related_ids: List[str] = Field(default=[], description="IDs of related documents")
    
    # Status fields
    is_archived: bool = Field(default=False, description="Whether document is archived")
    last_accessed: Optional[datetime] = Field(None, description="Last time document was accessed")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "doc123",
                "title": "Meeting Notes - Q1 Planning",
                "content": "Discussion about Q1 goals and objectives...",
                "document_type": "note",
                "tags": ["meeting", "planning", "Q1"],
                "author": "john.doe@example.com",
                "summary": "Q1 planning meeting discussing key objectives and timelines",
                "is_archived": False
            }
        }