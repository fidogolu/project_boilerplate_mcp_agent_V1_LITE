# agent/state.py
"""AgentState — LangGraph state for the ReAct agent."""

from typing import Annotated, Optional

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class AgentState(TypedDict):
    # Chat history — add_messages reducer appends instead of overwriting
    messages: Annotated[list[BaseMessage], add_messages]

    # Final response extracted for Gradio display
    final_response: Optional[str]

    # Error propagation
    error: Optional[str]
