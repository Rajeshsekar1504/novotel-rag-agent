"""
agent/graph.py
------------------
Langgraph state machine - Wires nodes and edges into a compiled agent.

Graph topology:
    [START]
       ↓
    classify_intent
       ↓
    retrieve_documents
       ↓
    rerank_documents
       ↓
    generate_answer
       ↓
    should_retry? ──── YES (iteration < 1) ──→ retrieve_documents
       ↓ NO
     [END]
WHY Langgraph over a plain chain:
    - Conditional edges enable retry logic - impossible in a liner chain
    - State is explicit and inspectable at every step
    - Easy to add new nodes (e.g., tool calling, guardrails) later
    - Built-in support for streaming and async
"""
from langgraph.graph import StateGraph, END
from models.state import AgentState
from agent.nodes import(
    classify_intent,
    retrieve_documents,
    rerank_documents,
    generate_answer,
)
from agent.prompts import LOW_CONFIDENCE_PHRASES
from core.logging import setup_logger

logger = setup_logger(__name__)

# ── Conditional Edge Function ─────────────────────────────────────────────────

def should_retry(state: AgentState) -> str:
    """
    Router called after generate_answer.
    Returns "retry" to look back to retrieval, or "end" to finish.

    Retry conditions:
        - Answer contains a low-confidence phrase
        - And we haven't already retried (max 1 retry)
    """
    answer = state.get("answer", "")
    iterations = state.get("iteration_count", 0)

    answer_lower = answer.lower()
    is_low_confidence = any(
        phrase in answer_lower for phrase in LOW_CONFIDENCE_PHRASES
    )

    if is_low_confidence and iterations < 2:
        logger.info(f"Low confidence detected - retrying retrieval (iteration{iterations})")
        return "retry"
    
    logger.info(f"Answer accepted - finishing (iteration{iterations})")
    return "end"

# ── Build Graph ───────────────────────────────────────────────────────────────

def build_agent():
    """
    Constructs and compiles the Langgraph agent.
    Returns a compiled graph ready to invoke.

    Usage:
         agent = build_agent()
         result = agent.invoke(initial_state)
    """
    graph = StateGraph(AgentState)

    # ── Register nodes ────────────────────────────────────────────────────────
    graph.add_node("classify_intent", classify_intent)
    graph.add_node("retrieve_documents", retrieve_documents)
    graph.add_node("rerank_documents", rerank_documents)
    graph.add_node("generate_answer", generate_answer)

    # ── Entry point  ───────────────────────────────────────────────────────────
    graph.set_entry_point("classify_intent")

    # ── Linear edges  ──────────────────────────────────────────────────────────
    graph.add_edge("classify_intent", "retrieve_documents")
    graph.add_edge("retrieve_documents", "rerank_documents")
    graph.add_edge("rerank_documents", "generate_answer")
    
    # ── Conditional edge: retry or finish ─────────────────────────────────────
    graph.add_conditional_edges(
        "generate_answer",
        should_retry,
        {
            "retry": "retrieve_documents",   # Loop back with broader query
            "end": END,                      # Done - return result to caller
        }
    )
    compiled = graph.compile()
    logger.info("Langgraph agent compiled successfully")
    return compiled

# ── Singleton agent ───────────────────────────────────────────────────────────
# Compiled once at import time - not on every request.
agent = build_agent()