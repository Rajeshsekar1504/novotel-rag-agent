"""
rag/retriever.py
----------------
Vector store retriever using ChromaDB PersistentClient.
Compatible with ChromaDB 0.5.18.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_chroma import Chroma
from langchain_core.vectorstores import VectorStoreRetriever

from rag.embeddings import get_embedding_model
from core.logging import setup_logger
from core.exceptions import VectorStoreNotReadyError
from config import get_settings

logger   = setup_logger(__name__)
settings = get_settings()


def get_vectorstore() -> Chroma:
    """
    Load ChromaDB using PersistentClient — guaranteed to read from disk.
    """
    chroma_path = Path(settings.CHROMA_PATH)

    if not chroma_path.exists():
        raise VectorStoreNotReadyError()

    # Check sqlite file exists
    sqlite_file = chroma_path / "chroma.sqlite3"
    if not sqlite_file.exists():
        raise VectorStoreNotReadyError()

    embeddings = get_embedding_model()

    # Use PersistentClient directly — most reliable for 0.5.x
    client = chromadb.PersistentClient(
        path=str(chroma_path),
        settings=ChromaSettings(anonymized_telemetry=False)
    )

    vectorstore = Chroma(
        client=client,
        collection_name=settings.COLLECTION_NAME,
        embedding_function=embeddings,
    )

    count = vectorstore._collection.count()
    logger.info(
        f"Vector store loaded | "
        f"Collection: {settings.COLLECTION_NAME} | "
        f"Chunks: {count}"
    )

    return vectorstore


def get_retriever() -> VectorStoreRetriever:
    """
    Returns MMR retriever from the loaded vector store.
    """
    vectorstore = get_vectorstore()

    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k"           : settings.RETRIEVER_K,
            "fetch_k"     : settings.RETRIEVER_FETCH_K,
            "lambda_mult" : settings.RETRIEVER_LAMBDA,
        }
    )

    logger.info(
        f"Retriever ready | "
        f"k={settings.RETRIEVER_K} | "
        f"fetch_k={settings.RETRIEVER_FETCH_K} | "
        f"lambda={settings.RETRIEVER_LAMBDA}"
    )

    return retriever