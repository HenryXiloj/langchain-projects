import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from app.embeddings import build_embeddings
    from app.llm import build_llm
    from app.vectorstore import build_vectorstore
else:
    from .embeddings import build_embeddings
    from .vectorstore import build_vectorstore
    from .llm import build_llm

from langchain_core.prompts import ChatPromptTemplate


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def main():
    question = sys.argv[1] if len(sys.argv) > 1 else "What is pgvector used for?"

    embeddings = build_embeddings()
    vectorstore = build_vectorstore(embeddings)
    retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 3})

    docs = retriever.invoke(question)
    context = format_docs(docs)

    prompt = ChatPromptTemplate.from_template("""
Answer using ONLY the context.
If unknown, say: I don't know.

Context:
{context}

Question:
{question}
""")

    llm = build_llm()
    response = llm.invoke(prompt.format_messages(context=context, question=question))

    print("\nAnswer:\n", response.content)

    for i, d in enumerate(docs, 1):
        print(f"\nSource {i}: {d.metadata}")


if __name__ == "__main__":
    main()
