from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional

class CrawlRequest(BaseModel):
    root_url: HttpUrl
    max_pages: Optional[int] = Field(default=None, ge=1, le=5000)

class CrawlResponse(BaseModel):
    pages_processed: int
    chunks_indexed: int
    skipped_non_html: int
    visited_count: int

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[HttpUrl]
