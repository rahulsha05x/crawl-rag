from typing import Any
from .config import OPENAI_API_KEY, EMBEDDING_BACKEND

# Choose your embedding function
def get_embedding_fn() -> Any:
    """
    Returns a LangChain-compatible embedding function.
    Default: OpenAI. Optional: sentence-transformers (local, no key).
    """
    if EMBEDDING_BACKEND.lower() == "local":
        # pip install sentence-transformers
        from langchain_community.embeddings import HuggingFaceEmbeddings
        return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    else:
        # OpenAI (recommended for quality)
        from langchain_openai import OpenAIEmbeddings
        if not OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY missing. Set it or switch EMBEDDING_BACKEND=local.")
        return OpenAIEmbeddings(model="text-embedding-3-small")
