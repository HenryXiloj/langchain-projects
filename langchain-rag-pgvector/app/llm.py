from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from .config import require_env, require_provider
import os

def build_llm():
    provider = require_provider("LLM_PROVIDER", "openai")
    model = os.getenv("LLM_MODEL")

    if provider == "openai":
        return ChatOpenAI(
            api_key=require_env("OPENAI_API_KEY"),
            model=model or "gpt-4o-mini",
            temperature=0.2,
        )

    return ChatOllama(
        model=model or "deepseek-r1:1.5b",
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=0.2,
    )
