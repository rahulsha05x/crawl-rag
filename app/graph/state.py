from typing import TypedDict, List, Dict

class RAGState(TypedDict):
    query: str
    retrieved: List[Dict]   # raw docs (content + metadata)
    answer: str
    sources: List[str]      # list of URLs
