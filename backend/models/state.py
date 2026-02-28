"""
models/state.py
-------------------
Langgraph agent state definition.

WHY TypedDict for state:
      Langgraph passes state between nodes as a dictionary.
      TypedDict gives us type hints and IDE autocomplete without
      the overhead of Pydantic (LangGraph handles itw own serialization).
How state flows:
      Entry -> classify_intent -> retrieved_documents -> rerank -> generate_answer -> END
                                      ↑                              |
                                      └──────── retry (if low conf)  ┘
Each node receives the full state dict and returns a partial dict
with only the keys it modified. LangGraph merges them automatically.
"""

from typing import TypedDict, Annotated, List, Optional
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    """
    Complete state object passed between all LangGraph nodes.

    messages:
          Full conversation history as LangChain message objects.
          Annotated with operator.add so each node APPENDS to the list
          instead of replacing it. This is LangGraph's merge strategy.
    session_id:
          Ties this invocation to a user session for memory persistence.
    
    user_query:
          The raw query from the current turn.
    intent:
          Classified intent - set by classify_intent node.
          Used to enrich the retrieval query for better precision.
    retrieved_docs:
          Raw chunks from MMR retrieval - set by retrieve_documents node.
    
    reranked_docs:
          Subset of retrieved_docs after reranking - set by rerank node.
    
    answer: 
        Final generated answer - set by generate_answer node.
    
    sources:
        List of source metadata dicts to run to frontend.

    needs_escalation:
        True if user asked for a human agent or used complaint keywords.

    iteration_count:
        Tracked retries. Max 1 retry to avoid infinite loop.
    """

    messages: Annotated[List[BaseMessage], operator.add]
    session_id: str
    user_query: str
    intent: Optional[str]
    retrieved_docs: List[dict]
    reranked_docs: List[dict]
    answer: Optional[str]
    sources: List[dict]
    needs_escalation: bool
    iteration_count: int