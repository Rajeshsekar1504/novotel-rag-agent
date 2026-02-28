"""
rag/reranker.py
---------------
Cross-encoder reranking to improve retrieval precision.

WHY reranking:
       MMR retrieval is fast but uses embedding similarity - a coarse measure.
       A cross-encoder reads the query and chunk together, giving a much more
       accurate relevance score. We retrieve k=5 chunks with MMR, then rerank
       and keep only top_n=3, ensuring the LLM gets the highest quality context.
Pipeline:
    Query->MMR Retrieval (k=5) -> Reranker -> Top N chunks->LLM

Two reranking strategies provided
    1.LLMReranker - Uses GPT to score relevances (accurate, costs tokens)
    2.CrossEncoderReranker - Uses a local HuggingFace model(free, fast)

Default: LLMReranker (no extra dependencies needed for this project)               
"""

from typing import List
from langchain.schema import Document
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from config import get_settings
from core.logging import setup_logger

logger = setup_logger(__name__)
settings = get_settings()

# ── LLM-Based Reranker

class LLMReranker:
    """
    Uses GPT to score how relevant each chunk is to the query.
    Scores chunks 1-10 and returns top_n highest-scored chunks.

    Cost: Small - uses gpt-4o-mini with very short prompts.
    Accuracy: High -- LLM understands semantic nuance.
    """

    def __init__(self, top_n: int = None):
        self.top_n = top_n or settings.RERANKER_TOP_N
        self.llm = ChatOpenAI(
            model=settings.CHAT_MODEL,
            temperature=0,
            openai_api_key=settings.OPENAI_API_KEY
            
        )
    
    def rerank(self, query: str, documents: List[Document]) ->List[Document]:
        """
        Score each document and return top_n sorted by relevance.

        Args:
            query: The user's original question
            documents: List of retrieved Document chunks

        Returns:
            Top N documents sorted by relevance score(highest first)
        """
        if not documents:
            return []
        
        scored = []

        for doc in documents:
            prompt = f"""Rate how relevant this text is to answering
Query: {query}
Text: {doc.page_content[:500]}

Respond with ONLY a number from 1 to 10.
10 = perfectly answer the query
1 = completely irrelevant
Number:"""
            try:
                response = self.llm.invoke([HumanMessage(content=prompt)])
                score = float(response.content.strip())
            except Exception:
                score = 5.0   # Default neutral score on failure

            scored.append((score, doc))
            logger.debug(f"Chunk score: {score:.1f} | {doc.page_content[:60]}...")

        # Sort descending by score, return top_n
        scored.sort(key=lambda x: x[0], reverse=True)
        top_docs = [doc for _, doc in scored[:self.top_n]]

        logger.info(
            f"Reranked {len(documents)} chunks -> kept top {len(top_docs)} | "
            f"Top score: {scored[0][0]:.1f}"
        )   
        
        return top_docs
    
# ── Cross-Encoder Reranker (Optional — No API cost) ───────────────────────────

# class CrossEncoderReranker:
#     """
#     Uses a local HuggingFace cross-encoder model.
#     No API cost. Runs on CPU. Slightly slower than LLMReranker.

#     Requires: pip install sentence-transformers
#     Model: cross-encoder/ms-marco-MiniLM-L-6-v2 (fast, accurate)

#     Usuage:
#          reranker = CrossEncoderReranker()
#          top_docs = reranker.rerank(query, documents)
#     """

#     def __init__(self, top_n: int = None):
#         self.top_n = top_n or settings.RERANKER_TOP_N
#         self._model = None # Lazy load - only import if this is used

#     def _load_model(self):
#         if self._model is None:
#             try:
#                 from sentence_transformers import CrossEncoder
#                 self._model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
#                 logger.info("CrossEncoder model loaded")
#             except ImportError:
#                 raise ImportError(
#                     "sentence-transformers not installed."
#                     "Run: pip install sentence-transformers"
#                 )
    
#     def rerank(self, query: str, documents: List[Document]) -> List[Document]:
#         self._load_model()

#         if not documents:
#             return []
        
#         pairs = [[query, doc.page_content] for doc in documents]
#         scores = self._model.predict(pairs)

#         scored = list(zip(scores, documents))
#         scored.sort(key=lambda x: x[0], reverse=True)
#         top_docs = [doc for _, doc in scored[:self.top_n]]

#         logger.info(f"CrossEncoder reranked {len(documents)} →{len(top_docs)} chunks")
#         return top_docs

# ----Factory -- get default reranker

def get_reranker() -> LLMReranker:
    """
    Returns  the default reranker instance.

    Swithch to CrossEncoderReranker() here if you want zero API cost
reranking
    Usage:
         from rag.reranker import get_reranker
         reranker = get_reranker()
         top_docs = reranker.rerank(query, retrieved_docs)
    """
    return LLMReranker(top_n=settings.RERANKER_TOP_N)

    
            
    
    
    
    
        


