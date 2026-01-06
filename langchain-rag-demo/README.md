# LangChain RAG Demo

A demonstration project showcasing Retrieval-Augmented Generation (RAG) using LangChain, OpenAI, and Pinecone vector database.

## Overview

This project demonstrates how to:
1. Load documents and split them into chunks
2. Create embeddings using OpenAI
3. Store embeddings in Pinecone vector database
4. Retrieve relevant context and generate answers using RAG

## Prerequisites

- Python 3.13 or higher
- OpenAI API key
- Pinecone API key and index

## Installation

1. Clone or navigate to this project directory

2. Install dependencies using `uv`:
   ```bash
   uv sync
   ```

   Or using pip:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Create a `.env` file in the project root with the following environment variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1  # Optional: custom endpoint
OPENAI_MODEL=gpt-4  # or gpt-3.5-turbo, gpt-4o, etc.

# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=your_index_name_here
```


## Usage

### Step 1: Load Data to Vector Database

**Run this first** to load your documents into the Pinecone vector database:

```bash
python load_file_to_vector_db.py
```

This script will:
- Load the `example_pinecone.txt` file
- Split the text into chunks (1000 characters each)
- Generate embeddings using OpenAI
- Store the embeddings in your Pinecone index

### Step 2: Query the RAG System

**Run this second** to query the vector database and get AI-generated answers:

```bash
python main.py
```

This script will:
- Connect to your Pinecone vector database
- Retrieve the top 3 most relevant document chunks for the question
- Use OpenAI to generate an answer based on the retrieved context
- Display the question and answer

## Project Structure

```
langchain-rag-demo/
├── load_file_to_vector_db.py  # Step 1: Load documents to vector DB
├── main.py                     # Step 2: Query and generate answers
├── example_pinecone.txt        # Sample document about Pinecone
├── pyproject.toml              # Project dependencies
├── .env                        # Environment variables (not in repo)
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## How It Works

### Document Loading & Embedding (`load_file_to_vector_db.py`)

1. **Load Document**: Reads the text file using `TextLoader`
2. **Split Text**: Divides the document into manageable chunks using `CharacterTextSplitter`
3. **Create Embeddings**: Converts text chunks into vector embeddings using OpenAI's embedding model
4. **Store in Pinecone**: Saves the embeddings to Pinecone for fast similarity search

### RAG Query System (`main.py`)

1. **Initialize Components**: Sets up OpenAI LLM, embeddings, and Pinecone vector store
2. **Retrieve Context**: Searches for the top 3 most relevant document chunks based on the question
3. **Generate Answer**: Uses a prompt template to instruct the LLM to answer based only on retrieved context
4. **Display Results**: Shows the question and AI-generated answer

## Customization

### Change the Question

Edit the `question` variable in `main.py`:

```python
question = "Your custom question here"
```

### Adjust Retrieval Settings

Modify the number of retrieved documents in `main.py`:

```python
retrieved_docs = vectorstore.as_retriever(search_kwargs={"k": 5})  # Retrieve top 5 instead of 3
```

### Change Chunk Size

Adjust text splitting parameters in `load_file_to_vector_db.py`:

```python
text_splitter = CharacterTextSplitter(
    chunk_size=500,      # Smaller chunks
    chunk_overlap=50,    # Add overlap between chunks
)
```

### Use Your Own Documents

Replace `example_pinecone.txt` with your own text file, or modify the `file_path` variable in `load_file_to_vector_db.py`:

```python
file_path = BASE_DIR / "your_document.txt"
```

## Dependencies

- **langchain**: Core LangChain framework
- **langchain-community**: Community integrations
- **langchain-openai**: OpenAI integration for LLMs and embeddings
- **langchain-pinecone**: Pinecone vector store integration
- **python-dotenv**: Environment variable management
- **black**: Code formatting
- **isort**: Import sorting

## Troubleshooting

### "No API key provided" Error
- Ensure your `.env` file exists and contains valid API keys
- Check that environment variables are loaded correctly

### "Index not found" Error
- Verify your Pinecone index name is correct
- Ensure the index exists in your Pinecone account
- Check that the index dimensions match your embedding model (OpenAI: 1536 dimensions)

### "No documents found" Error
- Make sure you ran `load_file_to_vector_db.py` first
- Verify that documents were successfully loaded to Pinecone


## Resources

- [LangChain Documentation](https://python.langchain.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Pinecone Documentation](https://docs.pinecone.io/)
