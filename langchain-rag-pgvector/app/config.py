import os
from dotenv import load_dotenv

load_dotenv()

def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value

def env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}

def require_provider(name: str, default: str) -> str:
    value = os.getenv(name, default).strip().lower()
    if value not in {"openai", "ollama"}:
        raise RuntimeError(f"{name} must be either 'openai' or 'ollama'")
    return value
