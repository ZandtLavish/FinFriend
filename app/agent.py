from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.messages import SystemMessage
from typing import TypedDict, Annotated
import operator
import logging
logger = logging.getLogger(__name__)

from app.tools import (
    get_ticker_price,
    get_macro_indicator,
    search_fred_series
)
from app.chroma_client import get_vector_store
from app.constants import KNOWN_SERIES
from app.config import settings

# Agent state definition
class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    context: str

# Vector Store
embeddings = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url=settings.OLLAMA_HOST
)
retriever = get_vector_store().as_retriever(search_kwargs={"k": 5})

tools = [
    get_ticker_price,
    get_macro_indicator,
    search_fred_series
]

logging.debug(f"Loading LLM Model: {settings.LLM_MODEL} ({settings.OLLAMA_HOST})")

llm = ChatOllama(
    model=settings.LLM_MODEL,
    base_url=settings.OLLAMA_HOST,
    temperature=0
).bind_tools(tools)


def retrieve_node(state: AgentState) -> AgentState:
    """Retrieve context from vector store (Chroma)"""
    logger.debug("Starting Retrieve Node")
    
    query = state["messages"][-1].content
    docs = retriever.invoke(query)
    context = "\n\n".join([d.page_content for d in docs])
    
    return {"context": context}


def agent_node(state: AgentState) -> AgentState:
    logger.debug("Starting Agent Node")

    content = f"""You are a financial research assistant.
Use the retrieved context for historical, qualitative, or document-based questions.
Use tools for real-time data (prices, rates, recent filings).
Always cite the source of your information and specify if you don't have a reputable source directly drawn from.
Never fabricate values you're intended to retrieve.

When retrieving macroeconomic data, follow this decision process:
1. If the user's request clearly maps to a known series ID, call
   get_macro_indicator directly with that ID.
2. If you are uncertain which series ID to use, call search_fred_series
   first, then pass the most relevant resulting series ID to get_macro_indicator.
3. Never construct or guess a series ID — only use IDs returned by
   search_fred_series or from the known list below.
4. Prefer the most specific series available. For inflation, prefer core measures
  (CPILFESL, PCEPILFE) unless the user explicitly asks for headline figures.
5. After retrieving a value, always state the series name, value, and date
  in your response so the user knows what was retrieved.

Known FRED series IDs:
{"\n".join(f"  - {sid}: {desc}" for sid, desc in KNOWN_SERIES.items())}

Retrieved context:
{state.get('context', 'None')}
"""

    system = SystemMessage(content=content)
    response = llm.invoke([system] + state["messages"])
    
    return {"messages": [response]}

def should_continue(state: AgentState) -> str:
    """Determine if should call a tool or end inference"""
    logger.debug("Starting tool-determining node")
    
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return END

# Graph
graph = StateGraph(AgentState)

graph.add_node("retrieve", retrieve_node)
graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode(tools))

graph.set_entry_point("retrieve")
graph.add_edge("retrieve", "agent")
graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
graph.add_edge("tools", "agent")

app = graph.compile()