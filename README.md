# 📡 NovaTel RAG Agent

Production-grade Retrieval-Augmented Generation (RAG) system for telecom customer support.
Built using FastAPI, LangChain, LangGraph, OpenAI embeddings, ChromaDB, and React.

This system ingests telecom knowledge base documents (.docx), generates embeddings, stores them in ChromaDB, and serves grounded answers via an AI agent.

---

# 🚀 Features

## RAG System

* DOCX knowledge base ingestion
* Incremental indexing using file hashing
* Automatic detection of new/changed documents
* Removal of deleted document embeddings
* Persistent Chroma vector database
* Deterministic chunk IDs (idempotent ingestion)

## Backend

* FastAPI production API
* LangGraph agent orchestration
* Modular architecture
* Structured logging

## Frontend

* React + Vite chat interface
* Real-time responses
* Source attribution

## DevOps

* Conda environment
* Shell automation scripts
* Logging system
* Docker support

---

# 📂 Project Structure

```
novotel-rag-agent/
│
├── .github/
├── backend/
│   ├── rag/
│   ├── agent/
│   ├── logs/
│   ├── main.py
│   └── requirements.txt
│
├── chroma_db/              # Vector database
├── documents/              # Knowledge base DOCX files
├── frontend/               # React frontend
├── infra/                  # Infrastructure configs
├── scripts/                # Automation scripts
│
├── novotel-rag/            # Conda environment
│
├── .env
├── hash_registry.json
└── README.md
```

---

# ⚙️ Environment Setup

You already created a conda environment inside project:

```
novotel-rag/
```

Activate it:

```
conda activate D:/novotel-rag-agent/novotel-rag
```

Verify:

```
python --version
```

---

# 📦 Install Dependencies

Backend:

```
pip install -r backend/requirements.txt
```

Frontend:

```
cd frontend
npm install
cd ..
```

---

# 🔐 Environment Variables

Create `.env`

```
OPENAI_API_KEY=your_key_here
ANONYMIZED_TELEMETRY=False
```

---

# 📥 Knowledge Base Ingestion

Place DOCX files in:

```
documents/
```

Run ingestion:

```
./scripts/ingest.sh
```

This will:

• detect new files
• generate embeddings
• update vector database

---

# ▶ Start Backend

```
./scripts/start_backend.sh
```

Runs at:

```
http://localhost:8000
```

---

# ▶ Start Frontend

```
./scripts/start_frontend.sh
```

Runs at:

```
http://localhost:5173
```

---

# 🔄 Restart System

```
./scripts/restart.sh
```

---

# 🛑 Stop System

```
./scripts/stop.sh
```

---

# 🧪 Test Vector Database

```
python backend/rag/test.py
```

Shows total indexed chunks.

---

# 📊 Logs

Located at:

```
backend/logs/
```

Includes:

```
rag_system.log
backend.pid
frontend.pid
```

---

# 🧠 System Architecture

```
DOCX files
   ↓
Ingestion pipeline
   ↓
OpenAI embeddings
   ↓
Chroma vector database
   ↓
Retriever
   ↓
LangGraph agent
   ↓
FastAPI backend
   ↓
React frontend
```

---

# ⚡ Performance

Typical ingestion:

```
40 chunks → 30–90 seconds
```

Query response:

```
< 1 second
```

---

# 🐳 Docker (optional)

Build:

```
docker build -t novotel-rag .
```

Run:

```
docker compose up
```

---

# 📌 Production Features Implemented

Incremental indexing
File hashing
Persistent vector DB
Deterministic chunk IDs
Script automation
Logging
Frontend + Backend separation

---

# 👨‍💻 Author

NovaTel RAG Agent
Production-grade telecom support AI system
