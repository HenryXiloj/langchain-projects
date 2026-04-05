# 🧠 LangChain RAG with PGVector

A simple **Retrieval-Augmented Generation (RAG)** demo powered by PostgreSQL + pgvector, LangChain, and Ollama — runs fully local, no API keys needed.

---

## How It Works

```
User Question
     │
     ▼
┌─────────────────────┐
│     Embedding       │  Convert question → vector
└─────────────────────┘
     │
     ▼
┌─────────────────────┐
│ PostgreSQL/pgvector │  Semantic similarity search
│   (Vector Store)    │  Returns top-K relevant chunks
└─────────────────────┘
     │
     ▼
┌─────────────────────┐
│  LLM (Ollama /      │  Generates answer from context
│     OpenAI)         │
└─────────────────────┘
     │
     ▼
   Final Answer
```

---

## Features

| Feature | Description |
|---|---|
| 🗄️ **pgvector** | PostgreSQL-native vector similarity search |
| 🔗 **LangChain** | Composable RAG pipeline |
| 🤖 **deepseek-r1:1.5b** | Default local LLM via Ollama |
| 🔤 **nomic-embed-text** | Default embedding model via Ollama |
| 🔀 **MMR Retrieval** | Maximal Marginal Relevance for diverse, high-quality results |
| ✂️ **Recursive Splitting** | Context-aware chunking for better retrieval |
| 🏷️ **Metadata Support** | Tag and filter documents by source, date, or custom fields |
| 🧩 **Modular Design** | Clean separation: config, embeddings, LLM, vectorstore |
| 🖥️ **CLI Interface** | Ask questions directly from the terminal |
| 🔒 **Fully Local** | Runs entirely offline — no API keys needed |

---

## Setup

### 1. Install dependencies

```bash
uv venv --python 3.13
uv sync
```

### 2. Start pgvector with Docker (or Podman)

```bash
# Docker
docker compose -f docker-compose.yml up -d

# Podman (optional alternative)
podman compose -f docker-compose.yml up -d
```

> Uses the `pgvector/pgvector:pg17` image — the `vector` extension is pre-installed, no extra config needed.

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
# PostgreSQL connection
PGVECTOR_DATABASE_URL=postgresql+psycopg://langchain:langchain@localhost:6024/langchain
PGVECTOR_COLLECTION_NAME=langchain_docs
PGVECTOR_CREATE_EXTENSION=false

# LLM & Embedding providers
LLM_PROVIDER=ollama
EMBEDDING_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434

# Models
LLM_MODEL=deepseek-r1:1.5b
EMBEDDING_MODEL=nomic-embed-text
```

### 4. Ingest your documents

```bash
uv run python app/ingest.py
```

This loads your documents, splits them into chunks, embeds them, and stores everything in PostgreSQL.

### 5. Ask questions

```bash
uv run python app/ask.py "What is pgvector used for?"
```

---

## Project Structure

```
langchain-rag-pgvector/
├── app/
│   ├── __init__.py
│   ├── ask.py           # CLI query interface
│   ├── config.py        # Environment variables and settings
│   ├── embeddings.py    # Embedding model setup
│   ├── ingest.py        # Document loading and indexing
│   ├── llm.py           # LLM provider (Ollama / OpenAI)
│   └── vectorstore.py   # pgvector connection and retrieval
├── .env                 # Your local secrets (not committed)
├── .env.example         # Template for environment variables
├── docker-compose.yml   # pgvector PostgreSQL container
├── example_pgvector.txt # Sample document for testing ingestion
├── pyproject.toml       # Project dependencies (uv)
├── uv.lock              # Lockfile for reproducible installs
└── README.md
```

---

## RAG Pipeline — Deep Dive

```
 INGEST FLOW                         QUERY FLOW
 ───────────────────────             ──────────────────────────
 Documents (PDF, txt, …)             User types a question
       │                                      │
       ▼                                      ▼
 RecursiveTextSplitter              nomic-embed-text (Ollama)
 (chunk_size, overlap)              (same model as ingest)
       │                                      │
       ▼                                      ▼
 nomic-embed-text (Ollama)          pgvector similarity search
                                    (MMR for diverse results)
       │                                      │
       ▼                                      ▼
 PostgreSQL + pgvector              Top K chunks → LLM context
 collection: langchain_docs                   │
                                              ▼
                                    deepseek-r1:1.5b (Ollama)
                                    generates final answer
```

**Why MMR?** Standard similarity search can return near-duplicate chunks. Maximal Marginal Relevance balances relevance *and* diversity — giving the LLM richer, more varied context.

---


## Requirements

- Python 3.13+
- Docker (for pgvector on port `6024`)
- [uv](https://github.com/astral-sh/uv) package manager
- [Ollama](https://ollama.com) with `deepseek-r1:1.5b` and `nomic-embed-text` pulled

```bash
ollama pull deepseek-r1:1.5b
ollama pull nomic-embed-text
```