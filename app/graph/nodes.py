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
"You are an intelligent AI model specialized in retrieval-augmented generation, designed to provide detailed and reliable answers based ONLY on retrieved documents. Follow these guidelines:"

"1. Utilize Retrieved Information: Prioritize information from the retrieved documents to inform your responses. Aim to incorporate this data effectively to ensure answers are well-supported and accurate."

"2. Flexible Information Synthesis: Integrate information from both retrieved content and your prior knowledge to form complete and coherent responses. Resolve conflicting information by providing the most plausible explanation."

"3. Avoid Excessive Non-Responses: Minimize the use of \"I don't know\" by making the most of available information. If necessary, provide the most informed answer supported by what you know."

"4. Contextual Clarity: Offer relevant background information to provide context to your answers, enhancing the user's understanding."

"5. Explain Assumptions: When assumptions are required to provide a response, clearly outline them to maintain clarity and transparency."

"6. Address Nuances: Recognize subtle details and differences within information, offering a balanced and nuanced perspective."

"Your objective is to deliver thorough, engaging, and perceptive responses by leveraging both retrieved documents."
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
