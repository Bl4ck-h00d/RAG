from pydantic import BaseModel
from typing import Optional, List

class QueryRequest(BaseModel):
    query: str
    limit: Optional[int] = 3


# Response models
class DocumentMetadata(BaseModel):
    filename: str
    total_chunks: int
    # Allow additional fields

    class Config:
        extra = "allow"


class ChunkResult(BaseModel):
    content: str
    metadata: DocumentMetadata
    score: float
    doc_id: str
    chunk_id: int
    file_type: str


class QueryResponse(BaseModel):
    query: str
    results: List[ChunkResult]
