from typing import List
from langchain_openai import ChatOpenAI
from langchain.schema import AIMessage
from langchain_community.vectorstores import Chroma
import logging
from app.config import OPENAI_API_KEY
from app.vectorstore import get_chroma
from .state import RAGState

logging.basicConfig(level=logging.INFO)
# LLM (you can swap to other providers easily)
llm = ChatOpenAI(model="gpt-4o", temperature=0)

SYSTEM_PROMPT = (
    "You are a strict knowledge assistant. "
    "Answer ONLY using the provided context. "
    "If the context does not contain an answer, say: "
    "\"I cannot answer this from the current knowledge base.\""
)

def retrieve_node(state: RAGState) -> RAGState:
    db: Chroma = get_chroma()
    retriever = db.as_retriever(search_kwargs={"k": 4})
    docs = retriever.get_relevant_documents(state["query"])

    # store both content & metadata for citations
    state["retrieved"] = [{"text": d.page_content, "metadata": d.metadata} for d in docs]
    return state

def generate_node(state: RAGState) -> RAGState:
    # Build context
    context_blocks: List[str] = []
    for d in state["retrieved"]:
        src = d["metadata"].get("source", "")
        context_blocks.append(f"[Source: {src}]\n{d['text']}")
    context = "\n\n---\n\n".join(context_blocks) if context_blocks else "(no context)"

    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {state['query']}\n"
        f"Answer with short, precise sentences. Include inline markdown links [like this](URL) when citing a source."
    )
    logging.info(f"prompt: {prompt}")  # <--- Log the crawled page
    msg: AIMessage = llm.invoke(prompt)
    state["answer"] = msg.content

    # collect unique sources for explicit return
    sources = []
    for d in state["retrieved"]:
        src = d["metadata"].get("source")
        if src and src not in sources:
            sources.append(src)
    state["sources"] = sources

    return state
