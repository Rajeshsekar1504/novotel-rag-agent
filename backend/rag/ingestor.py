"""
rag/ingestor.py - Compatible with ChromaDB 0.5.18
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from typing import List

BACKEND_DIR  = Path(__file__).resolve().parent.parent
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BACKEND_DIR))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from config import get_settings
from core.logging import setup_logger

logger   = setup_logger(__name__)
settings = get_settings()

DOCS_PATH       = Path(settings.DOCS_PATH)
CHROMA_PATH     = Path(settings.CHROMA_PATH)
HASH_REGISTRY   = Path(settings.HASH_REGISTRY_PATH)
COLLECTION_NAME = settings.COLLECTION_NAME
CHUNK_SIZE      = 1000
CHUNK_OVERLAP   = 200
BATCH_SIZE      = 100


def compute_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def compute_file_hash(docs: List[Document]) -> str:
    return compute_hash(" ".join([d.page_content for d in docs]))


def load_hash_registry() -> dict:
    if HASH_REGISTRY.exists():
        with open(HASH_REGISTRY) as f:
            return json.load(f)
    return {}


def save_hash_registry(registry: dict) -> None:
    with open(HASH_REGISTRY, "w") as f:
        json.dump(registry, f, indent=2)


def infer_category(filename: str) -> str:
    mapping = {
        "Plans": "plans_pricing", "Billing": "billing",
        "Network": "network", "SIM": "sim_activation",
        "Roaming": "roaming", "Refund": "refund_cancellation",
    }
    for key, val in mapping.items():
        if key in filename:
            return val
    return "general"


def validate_environment() -> None:
    logger.info("Validating environment...")
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or api_key.startswith("sk-your"):
        logger.error("OPENAI_API_KEY missing"); sys.exit(1)
    if not DOCS_PATH.exists():
        logger.error(f"Documents folder not found: {DOCS_PATH}"); sys.exit(1)
    if not list(DOCS_PATH.glob("*.docx")):
        logger.error("No .docx files found"); sys.exit(1)
    logger.info(f"Valid | Docs: {len(list(DOCS_PATH.glob('*.docx')))} | Chroma: {CHROMA_PATH}")


def load_documents() -> List[Document]:
    old_registry = load_hash_registry()
    new_registry = {}
    all_docs: List[Document] = []

    for docx_path in sorted(DOCS_PATH.glob("*.docx")):
        filename = docx_path.name
        try:
            loader   = UnstructuredWordDocumentLoader(str(docx_path))
            raw_docs = loader.load()
        except Exception as e:
            logger.error(f"Failed: {filename}: {e}"); continue

        if not raw_docs:
            continue

        file_hash = compute_file_hash(raw_docs)
        new_registry[filename] = file_hash

        if old_registry.get(filename) == file_hash:
            logger.info(f"Unchanged — skipping: {filename}"); continue

        category = infer_category(filename)
        for doc in raw_docs:
            doc.metadata["source_file"] = filename
            doc.metadata["category"]    = category

        all_docs.extend(raw_docs)
        logger.info(f"Loaded: {filename} [{category}]")

    save_hash_registry(new_registry)
    logger.info(f"Loading complete | {len(all_docs)} pages")
    return all_docs


def split_documents(documents: List[Document]) -> List[Document]:
    if not documents:
        return []
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", "!", "?", ",", " "],
    )
    chunks = [c for c in splitter.split_documents(documents) if c.page_content.strip()]
    logger.info(f"Split into {len(chunks)} chunks")
    return chunks


def build_vector_store(chunks: List[Document]) -> None:
    logger.info(f"Creating ChromaDB at: {CHROMA_PATH}")
    CHROMA_PATH.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(
        path=str(CHROMA_PATH),
        settings=ChromaSettings(anonymized_telemetry=False)
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    embeddings_model = OpenAIEmbeddings(
        model=settings.EMBEDDING_MODEL,
        openai_api_key=settings.OPENAI_API_KEY,
    )

    total_batches = (len(chunks) + BATCH_SIZE - 1) // BATCH_SIZE

    for batch_num, start in enumerate(range(0, len(chunks), BATCH_SIZE), 1):
        batch   = chunks[start: start + BATCH_SIZE]
        texts   = [c.page_content for c in batch]
        metas   = [c.metadata for c in batch]
        ids     = [compute_hash(t) for t in texts]

        logger.info(f"Embedding batch {batch_num}/{total_batches} ({len(batch)} chunks)...")

        try:
            vectors = embeddings_model.embed_documents(texts)
            collection.upsert(ids=ids, embeddings=vectors, documents=texts, metadatas=metas)
            logger.info(f"Batch {batch_num} saved ✓")
        except Exception as e:
            logger.error(f"Batch {batch_num} failed: {e}", exc_info=True)
            break

    logger.info(f"Total in collection: {collection.count()}")


def ingest() -> None:
    logger.info("=" * 60)
    logger.info("  NovaTel RAG — Document Ingestion Pipeline")
    logger.info("=" * 60)

    validate_environment()
    documents = load_documents()

    if not documents:
        logger.info("No changes — skipping ingestion")
        try:
            client = chromadb.PersistentClient(path=str(CHROMA_PATH))
            col    = client.get_collection(COLLECTION_NAME)
            logger.info(f"Existing chunks: {col.count()}")
        except Exception:
            logger.info("No existing store found")
        return

    chunks = split_documents(documents)
    if not chunks:
        logger.warning("0 chunks — check document content")
        return

    build_vector_store(chunks)

    try:
        client = chromadb.PersistentClient(path=str(CHROMA_PATH))
        col    = client.get_collection(COLLECTION_NAME)
        total  = col.count()
    except Exception:
        total = len(chunks)

    logger.info("=" * 60)
    logger.info("  Ingestion complete!")
    logger.info(f"  Chunks this run : {len(chunks)}")
    logger.info(f"  Total in store  : {total}")
    logger.info(f"  Path            : {CHROMA_PATH}")
    logger.info("=" * 60)
    logger.info("Next step: uvicorn main:app --reload --port 8000")


if __name__ == "__main__":
    ingest()