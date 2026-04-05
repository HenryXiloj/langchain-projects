import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from app.embeddings import build_embeddings
    from app.vectorstore import build_vectorstore
else:
    from .embeddings import build_embeddings
    from .vectorstore import build_vectorstore

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

BASE_DIR = Path(__file__).resolve().parent.parent
FILE_PATH = BASE_DIR / "example_pgvector.txt"


def main():
    loader = TextLoader(FILE_PATH, encoding="utf8")
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    texts = splitter.split_documents(documents)

    for i, doc in enumerate(texts):
        doc.metadata["chunk_id"] = i

    embeddings = build_embeddings()
    vectorstore = build_vectorstore(embeddings)

    ids = [f"doc-{i}" for i in range(len(texts))]
    vectorstore.add_documents(texts, ids=ids)

    print("Ingest complete")


if __name__ == "__main__":
    main()
