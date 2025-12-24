# Import necessary libraries
import os
from dotenv import load_dotenv

# LangChain imports for creating agents and tools
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import HumanMessage

# OpenAI chat model integration
from langchain_openai import ChatOpenAI

# Tavily search integration - using native client
from tavily import TavilyClient


# Load environment variables from .env file
# This allows us to securely store API keys and configuration
load_dotenv()

# Initialize Tavily client
# Tavily is a search API optimized for LLMs and RAG applications
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# Define a custom tool using the @tool decorator
# This tool will be available for the agent to use when answering questions
@tool
def search(query: str) -> str:
    """
    Tool that searches over the internet using Tavily.
    
    This function uses Tavily's search API to find relevant information
    from the web to answer user queries.
    
    Args:
        query (str): The search query string.
    
    Returns:
        str: The search results from Tavily with sources.
    """
    print(f"Searching for: {query}")
    try:
        # Use Tavily client to perform the actual search
        response = tavily.search(query, max_results=5)
        
        # Format results to include content and sources
        formatted_results = []
        if 'results' in response:
            for idx, result in enumerate(response['results'], 1):
                formatted_results.append(
                    f"\n[Result {idx}]\n"
                    f"Title: {result.get('title', 'N/A')}\n"
                    f"URL: {result.get('url', 'N/A')}\n"
                    f"Content: {result.get('content', 'N/A')}\n"
                )
        
        return "\n".join(formatted_results) if formatted_results else str(response)
    except Exception as e:
        return f"Search error: {str(e)}"

# Initialize the ChatOpenAI language model
# This is the "brain" of our agent that will process queries and decide actions
llm = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),      # API key from environment variables
    #base_url=os.getenv("OPENAI_BASE_URL"),    # Optional: custom API endpoint
    model=os.getenv("OPENAI_MODEL"),          # Model name (e.g., "gpt-4", "gpt-3.5-turbo")
    temperature=0.2,                          # Lower temperature = more focused/deterministic responses
)

# Create a list of tools that the agent can use
# The agent will automatically decide when to use these tools based on the user's query
tools = [search]
#tools = [TavilyClient()]

# Create the agent using create_agent function
# The agent will use the LLM to reason about which tools to use and how to respond
agent = create_agent(model=llm, tools=tools)


def main():
    """
    Main function to run the LangChain search agent.
    
    This demonstrates how to:
    1. Create a user message
    2. Invoke the agent with the message
    3. Extract and display the agent's response
    """
    print("Welcome to the LangChain Search Agent!")
    print("=" * 80)
    
    # Invoke the agent with a user question
    # The input must be a dictionary with a 'messages' key containing a list of messages
    result = agent.invoke({
        "messages": [HumanMessage(content="What are the latest news about AI in December 2025?")]
    })
    
    # Display search sources used
    print("\n📚 Sources Used:")
    print("-" * 80)
    for idx, message in enumerate(result['messages']):
        if message.__class__.__name__ == 'ToolMessage' and hasattr(message, 'content'):
            # Extract URLs from the formatted results
            if 'URL:' in message.content:
                lines = message.content.split('\n')
                for line in lines:
                    if line.startswith('URL:'):
                        url = line.replace('URL:', '').strip()
                        if url != 'N/A':
                            print(f"  • {url}")
    
    # Extract the final response from the agent
    print("\n" + "=" * 80)
    print(f"\n🤖 Final Answer:\n{result['messages'][-1].content}")


if __name__ == "__main__":
    main()
