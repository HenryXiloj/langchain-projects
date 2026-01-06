import os
from dotenv import load_dotenv
from pathlib import Path

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent
file_path = BASE_DIR / "example_pinecone.txt"

def main():
    print("Hello from langchain-rag-demo!")

    # 1. Load document
    loader = TextLoader(
    file_path,
    encoding="utf8",
    )
    documents = loader.load()

    # 2. Split text
    text_splitter = CharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=0,
    )
    texts = text_splitter.split_documents(documents)
    print(f"Loaded {len(texts)} chunks")

    # 3. Create embeddings
    embeddings = OpenAIEmbeddings(
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    # 4. Store in Pinecone
    PineconeVectorStore.from_documents(
        texts,
        embeddings,
        pinecone_api_key=os.getenv("PINECONE_API_KEY"),
        index_name=os.getenv("PINECONE_INDEX_NAME"),
    )

    print("Vector store created successfully.")

if __name__ == "__main__":
    main()
