from langchain_postgres import PGVector
from .config import require_env, env_flag
import os

def build_vectorstore(embeddings):
    return PGVector(
        embeddings=embeddings,
        connection=require_env("PGVECTOR_DATABASE_URL"),
        collection_name=os.getenv("PGVECTOR_COLLECTION_NAME", "langchain_docs"),
        use_jsonb=True,
        create_extension=env_flag("PGVECTOR_CREATE_EXTENSION", False),
    )
