import os
from typing import List, Dict
from langchain_community.vectorstores import Chroma
from .embeddings import get_embedding_fn
from .config import CHROMA_DIR

def get_chroma() -> Chroma:
    """
    Load or create a persistent ChromaDB store.
    """
    os.makedirs(CHROMA_DIR, exist_ok=True)
    embedding_fn = get_embedding_fn()
    return Chroma(persist_directory=CHROMA_DIR, embedding_function=embedding_fn)

def add_documents_to_chroma(chunks: List[str], source_url: str):
    """
    Add chunks with metadata to Chroma (idempotent-ish; Chroma dedupes by content hash).
    """
    if not chunks:
        return 0
    db = get_chroma()
    metadatas: List[Dict] = [{"source": source_url, "chunk_id": i} for i, _ in enumerate(chunks)]
    db.add_texts(texts=chunks, metadatas=metadatas)
    db.persist()
    return len(chunks)


def get_chroma_collection(collection_name: str = "langchain") -> Chroma:
    """
    Load or create a persistent ChromaDB collection with the given name.
    """
    os.makedirs(CHROMA_DIR, exist_ok=True)
    embedding_fn = get_embedding_fn()
    return Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embedding_fn,
        collection_name=collection_name
    )