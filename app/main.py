from fastapi import FastAPI, BackgroundTasks, Depends,HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.models import CrawlRequest, CrawlResponse, QueryRequest, QueryResponse
from app.crawler import crawl_and_index
from app.graph.rag_graph import build_graph

app = FastAPI(title="FastAPI + LangGraph RAG (ChromaDB)")

# CORS (open by default; tighten in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# Build graph once (stateless between calls)
rag = build_graph()

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/crawl", response_model=CrawlResponse)
def crawl(req: CrawlRequest, background: BackgroundTasks):
    """
    Kick off a crawl+index. For long crawls, you can run it in background.
    Here we execute inline by default; uncomment background line to make async.
    """
    result = crawl_and_index(str(req.root_url), req.max_pages)
    # background.add_task(crawl_and_index, req.root_url, req.max_pages)  # optional
    return CrawlResponse(**result)

@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    """
    Answers strictly from embedded content; returns answer + list of source URLs.
    """
    initial_state = {
        "query": req.question,
        "retrieved": [],
        "answer": "",
        "sources": [],
    }
    final_state = rag.invoke(initial_state)

    # If we found no relevant docs, enforce safe fallback
    if not final_state["retrieved"] or "knowledge base" in final_state["answer"].lower():
        return QueryResponse(answer="I cannot answer this from the current knowledge base.", sources=[])

    return QueryResponse(answer=final_state["answer"], sources=final_state["sources"])

@app.delete("/embeddings")
def delete_embeddings(collection_name: str = Query(None, description="ChromaDB collection name (optional)")):
    """
    Delete all embeddings from ChromaDB.
    If collection_name is provided, delete from that collection; otherwise, delete from the default collection.
    """
    try:
        from app.vectorstore import get_chroma_collection
        collection = get_chroma_collection(collection_name) if collection_name else get_chroma_collection()
        collection.delete(where={"__all__": True})  # Delete all documents
        if collection_name:
            return {"detail": f"All embeddings deleted from ChromaDB collection '{collection_name}'."}
        else:
            return {"detail": "All embeddings deleted from the default ChromaDB collection."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))