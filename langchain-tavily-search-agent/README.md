# LangChain Tavily Search Agent

A powerful AI-powered search agent built with LangChain and Tavily Search API to find and synthesize information from the web. The agent intelligently decides when to search the internet and provides comprehensive answers with source citations.

## Features

- 🤖 **AI-Powered Agent**: Uses OpenAI's language models to understand queries and reason about when to search
- 🔍 **Web Search Integration**: Leverages Tavily Search API optimized for LLMs and RAG applications
- 📚 **Source Citations**: Automatically provides URLs and sources for all information retrieved
- 🛠️ **Custom Tools**: Extensible architecture allowing easy addition of new tools
- 🎯 **Formatted Results**: Clean, structured output with titles, URLs, and content snippets

## Prerequisites

- Python 3.13 or higher
- OpenAI API key
- Tavily API key

## Installation

1. Clone the repository or navigate to the project directory:
```bash
cd langchain-tavily-search-agent
```

2. Install dependencies using `uv` (recommended) or `pip`:

**Using uv:**
```bash
uv venv --python 3.13
uv sync
```

**Using pip:**
```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root with the following environment variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1  # Optional: custom API endpoint
OPENAI_MODEL=claude-sonnet-4-5

# Tavily Search API
TAVILY_API_KEY=your_tavily_api_key_here
```

### Getting API Keys

- **OpenAI API Key**: Sign up at [OpenAI Platform](https://platform.openai.com/)
- **Tavily API Key**: Sign up at [Tavily](https://tavily.com/)

## Usage

Run the agent:

```bash
python main.py
```

### Visual Studio Code Interpreter

If you want to run this project in Visual Studio Code, select the project venv:

1. Press `Ctrl+Shift+P`
2. Choose `Python: Select Interpreter`
3. Pick `langchain-tavily-search-agent\.venv\Scripts\python.exe`

The default example searches for "What are the latest news about AI in December 2025?" and displays:
- Source URLs used for the answer
- A comprehensive final answer synthesized from multiple sources

### Customizing the Query

Edit the `main()` function in `main.py` to change the search query:

```python
result = agent.invoke({
    "messages": [HumanMessage(content="Your custom question here")]
})
```

## Project Structure

```
langchain-tavily-search-agent/
├── main.py              # Main application with agent logic
├── pyproject.toml       # Project dependencies and metadata
├── README.md            # This file
├── .env                 # Environment variables (create this)
└── uv.lock             # Dependency lock file
```

## How It Works

1. **Agent Initialization**: The agent is created with a ChatOpenAI language model and custom search tools
2. **Query Processing**: When invoked, the agent analyzes the user's question
3. **Tool Selection**: The agent decides whether to use the search tool based on the query
4. **Web Search**: If needed, the Tavily API searches the web for relevant information (up to 5 results)
5. **Response Synthesis**: The agent synthesizes information from multiple sources into a coherent answer
6. **Output**: Results are displayed with source citations and a final answer

## Key Components

### Search Tool
The custom `@tool` decorated function provides web search capabilities:
- Searches using Tavily API
- Returns up to 5 results
- Formats results with titles, URLs, and content snippets
- Handles errors gracefully

### Language Model
- Uses OpenAI's ChatOpenAI with configurable model
- Temperature set to 0.2 for focused, deterministic responses
- Supports custom base URLs for alternative OpenAI-compatible endpoints

### Agent
- Created using LangChain's `create_agent` function
- Automatically reasons about tool usage
- Maintains conversation context through message history

## Dependencies

- **langchain** (>=1.2.0): Core LangChain framework
- **langchain-openai** (>=1.1.6): OpenAI integration
- **langchain-tavily** (>=0.2.15): Tavily search integration
- **tavily-python** (>=0.7.17): Tavily Python client
- **python-dotenv** (>=1.2.1): Environment variable management
- **black** (>=25.12.0): Code formatting
- **isort** (>=7.0.0): Import sorting

## Development

### Code Formatting

Format code using Black:
```bash
black main.py
```

Sort imports using isort:
```bash
isort main.py
```

### Extending the Agent

Add new tools by creating additional `@tool` decorated functions:

```python
@tool
def my_custom_tool(input: str) -> str:
    """Description of what this tool does."""
    # Your tool logic here
    return result

# Add to tools list
tools = [search, my_custom_tool]
```

## Example Output

```
Welcome to the LangChain Search Agent!
================================================================================

📚 Sources Used:
--------------------------------------------------------------------------------
  • https://example.com/ai-news-1
  • https://example.com/ai-news-2
  • https://example.com/ai-news-3

================================================================================

🤖 Final Answer:
Based on the latest information from December 2025, here are the key AI developments...
[Synthesized answer from multiple sources]
```

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure your `.env` file is properly configured with valid API keys
2. **Module Not Found**: Run `uv sync` or `pip install -r requirements.txt` to install dependencies
3. **Rate Limits**: Both OpenAI and Tavily have rate limits; consider implementing retry logic for production use

## Acknowledgments

- Built with [LangChain](https://langchain.com/)
- Powered by [OpenAI](https://openai.com/)
- Search by [Tavily](https://tavily.com/)
