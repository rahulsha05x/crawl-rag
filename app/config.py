import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
EMBEDDING_BACKEND = os.getenv("EMBEDDING_BACKEND", "openai")  # "openai" or "local"
CHROMA_DIR = os.getenv("CHROMA_DIR", "./chroma_store")

CRAWL_MAX_PAGES = int(os.getenv("CRAWL_MAX_PAGES", "200"))
CRAWL_DELAY_SECONDS = float(os.getenv("CRAWL_DELAY_SECONDS", "0.5"))

USER_AGENT = "Mozilla/5.0 (compatible; FastAPI-LangGraph-RAG/1.0)"
