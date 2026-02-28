"""
agent/nodes.py
--------------
Individual node functions for the LangGraph agent graph.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from typing import Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain.schema import Document                    # ← THIS was missing

from models.state import AgentState
from agent.prompts import (
    SYSTEM_PROMPT, INTENT_PROMPT, ANSWER_PROMPT,
    LOW_CONFIDENCE_PHRASES, ESCALATION_KEYWORDS
)
from rag.retriever import get_retriever
from rag.reranker import get_reranker
from config import get_settings
from core.logging import setup_logger

logger   = setup_logger(__name__)
settings = get_settings()

# ── Singletons ────────────────────────────────────────────────
llm = ChatOpenAI(
    model=settings.CHAT_MODEL,
    temperature=settings.TEMPERATURE,
    max_tokens=settings.MAX_TOKENS,
    openai_api_key=settings.OPENAI_API_KEY,
)
retriever = get_retriever()
reranker  = get_reranker()


# ── NODE 1: Classify Intent ───────────────────────────────────

def classify_intent(state: AgentState) -> dict:
    """
    Classifies user query into a telecom support category.
    Prepends intent to retrieval query for better precision.
    """
    query = state["user_query"]
    logger.info(f"Classifying intent for: '{query[:60]}'")

    prompt   = INTENT_PROMPT.format(query=query)
    response = llm.invoke([HumanMessage(content=prompt)])
    intent   = response.content.strip().lower()

    valid_intents = [
        "plans_pricing", "billing", "network",
        "sim_activation", "roaming", "refund_cancellation", "general"
    ]

    if intent not in valid_intents:
        intent = "general"

    logger.info(f"Intent: {intent}")
    return {"intent": intent}


# ── NODE 2: Retrieve Documents ────────────────────────────────

def retrieve_documents(state: AgentState) -> dict:
    """
    Retrieves relevant chunks from ChromaDB using MMR.
    On retry, broadens the query.
    """
    query     = state["user_query"]
    intent    = state.get("intent", "general")
    iteration = state.get("iteration_count", 0)

    enriched_query = query if iteration > 0 else f"[{intent}] {query}"

    logger.info(f"Retrieving | Query: '{enriched_query[:80]}'")

    docs: list[Document] = retriever.invoke(enriched_query)

    retrieved = [
        {
            "content"     : doc.page_content,
            "source_file" : doc.metadata.get("source_file", "Unknown"),
            "category"    : doc.metadata.get("category", "general"),
        }
        for doc in docs
    ]

    logger.info(f"Retrieved {len(retrieved)} chunks")
    return {
        "retrieved_docs"  : retrieved,
        "iteration_count" : iteration + 1,
    }


# ── NODE 3: Rerank Documents ──────────────────────────────────

def rerank_documents(state: AgentState) -> dict:
    """
    Reranks retrieved chunks for precision.
    """
    retrieved = state["retrieved_docs"]
    query     = state["user_query"]

    if not retrieved:
        return {"reranked_docs": []}

    docs = [
        Document(
            page_content=d["content"],
            metadata={
                "source_file": d["source_file"],
                "category"   : d["category"]
            }
        )
        for d in retrieved
    ]

    reranked = reranker.rerank(query, docs)

    reranked_dicts = [
        {
            "content"     : doc.page_content,
            "source_file" : doc.metadata.get("source_file", "Unknown"),
            "category"    : doc.metadata.get("category", "general"),
        }
        for doc in reranked
    ]

    logger.info(f"Reranked: {len(retrieved)} → {len(reranked_dicts)} chunks")
    return {"reranked_docs": reranked_dicts}


# ── NODE 4: Generate Answer ───────────────────────────────────

def generate_answer(state: AgentState) -> dict:
    """
    Generates grounded answer using reranked context.
    """
    docs  = state.get("reranked_docs") or state.get("retrieved_docs", [])
    query = state["user_query"]

    context = "\n\n---\n\n".join([
        f"[Source: {d['source_file']}]\n{d['content']}"
        for d in docs
    ])

    prompt = ANSWER_PROMPT.format(context=context, question=query)

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        *state.get("messages", []),
        HumanMessage(content=prompt),
    ]

    logger.info("Generating answer...")
    response = llm.invoke(messages)
    answer   = response.content.strip()

    needs_escalation = any(kw in query.lower() for kw in ESCALATION_KEYWORDS)

    if needs_escalation:
        logger.info("Escalation flag triggered")

    return {
        "answer"           : answer,
        "sources"          : docs,
        "needs_escalation" : needs_escalation,
        "messages"         : [
            HumanMessage(content=query),
            AIMessage(content=answer),
        ],
    }