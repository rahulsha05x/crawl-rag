from langgraph.graph import StateGraph, START, END
from .state import RAGState
from .nodes import retrieve_node, generate_node

def build_graph():
    g = StateGraph(RAGState)
    g.add_node("retrieve", retrieve_node)
    g.add_node("generate", generate_node)

    g.add_edge(START, "retrieve")
    g.add_edge("retrieve", "generate")
    g.add_edge("generate", END)

    return g.compile()
