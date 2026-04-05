from langchain_ollama import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings
from .config import require_env, require_provider
import os

def build_embeddings():
    provider = require_provider("EMBEDDING_PROVIDER", "openai")
    model = os.getenv("EMBEDDING_MODEL")

    if provider == "openai":
        return OpenAIEmbeddings(
            api_key=require_env("OPENAI_API_KEY"),
            model=model or "text-embedding-3-small",
        )

    return OllamaEmbeddings(
        model=model or "nomic-embed-text",
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    )
