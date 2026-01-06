import os
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

load_dotenv()

print("Hello from langchain-rag-demo!")

def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value

OPENAI_API_KEY = require_env("OPENAI_API_KEY")
PINECONE_API_KEY = require_env("PINECONE_API_KEY")
PINECONE_INDEX_NAME = require_env("PINECONE_INDEX_NAME")
OPENAI_MODEL = require_env("OPENAI_MODEL")

embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)

llm = ChatOpenAI(
    api_key=OPENAI_API_KEY,
    model=OPENAI_MODEL,
    temperature=0.2,
)

vectorstore = PineconeVectorStore(
    pinecone_api_key=PINECONE_API_KEY,
    index_name=PINECONE_INDEX_NAME,
    embedding=embeddings,
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

prompt_template = ChatPromptTemplate.from_template(
    """
    You are a helpful assistant.
    Use ONLY the following context to answer the question.
    If the answer is not in the context, say "I don't know".

    Context:
    {context}

    Question:
    {question}
    """
)


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

if __name__ == "__main__":
    question = "What is Pinecone used for?"

    docs = retriever.invoke(question)
    context = format_docs(docs)

    prompt = prompt_template.format_messages(
        context=context,
        question=question,
    )

    response = llm.invoke(prompt)

    print("Question:", question)
    print("Answer:", response.content)
