# agent/graph.py
"""ReAct agent — LangGraph graph definition.

Architecture:
    user_message → [check_input] → call_llm → [tool_node] → call_llm → ... → [check_output] → response

Conditional edges:
    call_llm → tools      if the LLM requested a tool call
    call_llm → end_node   if the LLM produced a final answer
"""

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

from agents.state import AgentState
from agents.tools import TOOLS
from utils.llm import WORKER_LLM
from utils.logger import LOGGER
from utils.security import check_input, check_output

_SYSTEM_PROMPT = """You are a helpful assistant with access to tools that can:
- Read, search, and manage files in a file system (read_file, list_directory, search_files)
- Search the web and fetch web pages (search_web, fetch_url)
- Write and manage text files (write_file, create_directory, rename_file)

Use the appropriate tools to answer the user's request.
Always think step by step before calling a tool.
When you have enough information, provide a clear and concise final answer.
"""

# Bind tools to LLM
_llm_with_tools = WORKER_LLM.bind_tools(TOOLS)


# ── Nodes ─────────────────────────────────────────────────────────────────────


async def check_input_node(state: AgentState) -> dict:
    """Apply security check on the latest user message."""
    if state.get("error"):
        return {}

    last_message = state["messages"][-1]
    text = (
        last_message.content if hasattr(last_message, "content") else str(last_message)
    )

    safe = check_input(text)
    if safe.is_blocked:
        LOGGER.warning("check_input_node blocked: %s", safe.reason)
        return {"error": f"Input blocked by security policy: {safe.reason}"}

    # Replace last message content with sanitized version
    from langchain_core.messages import HumanMessage

    return {"messages": [HumanMessage(content=safe.sanitized_text)]}


async def call_llm(state: AgentState) -> dict:
    """Call the LLM with the current message history."""
    if state.get("error"):
        return {}

    messages = [SystemMessage(content=_SYSTEM_PROMPT)] + state["messages"]

    try:
        response = await _llm_with_tools.ainvoke(messages)
        LOGGER.debug(
            "call_llm: tool_calls=%d", len(getattr(response, "tool_calls", []) or [])
        )
        return {"messages": [response]}
    except Exception as e:
        LOGGER.error("call_llm failed", exc_info=True)
        return {"error": str(e)}


async def check_output_node(state: AgentState) -> dict:
    """Apply security check on the LLM final response and extract it."""
    if state.get("error"):
        return {}

    last_message = state["messages"][-1]
    text = (
        last_message.content if hasattr(last_message, "content") else str(last_message)
    )

    safe = check_output(text)
    if safe.is_blocked:
        LOGGER.warning("check_output_node blocked: %s", safe.reason)
        return {"error": f"Output blocked by security policy: {safe.reason}"}

    return {"final_response": safe.sanitized_text}


# ── Conditional edge ──────────────────────────────────────────────────────────


def should_use_tools(state: AgentState) -> str:
    """Route to tools if the LLM made tool calls, otherwise finalize."""
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END


# ── Build graph ───────────────────────────────────────────────────────────────

workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("check_input", check_input_node)
workflow.add_node("call_llm", call_llm)
workflow.add_node("tools", ToolNode(TOOLS))
workflow.add_node("check_output", check_output_node)

# Set entry and edges
workflow.set_entry_point("check_input")
workflow.add_conditional_edges(
    "call_llm",
    should_use_tools,
    {
        "tools": "tools",
        END: "check_output",
    },
)
workflow.add_edge("check_input", "call_llm")
workflow.add_edge("tools", "call_llm")
workflow.add_edge("check_output", END)

graph = workflow.compile()
