# main.py
"""Gradio chat interface — entry point.

Calls the LangGraph ReAct agent and streams the response to the user.

Security controls at Gradio layer:
1. Input validation (message length check via MAX_MESSAGE_LENGTH)
2. Logging via existing LOGGER (utils/logger.py)

Agent layer security (preserved):
- LlamaFirewall semantic analysis (check_input_node)
- llm-guard output sanitization (check_output_node)

Rate limiting handled by Nginx proxy (per IP).
No API key field — authentication handled by Nginx Basic Auth.
"""

from dotenv import load_dotenv

load_dotenv()


import gradio as gr
from langchain_core.messages import HumanMessage

from agents.graph import graph
from config.constants import MAX_MESSAGE_LENGTH
from utils.logger import LOGGER


async def chat(user_message: str, history: list) -> str:
    """Handle a user message and return the agent's response.

    Security controls at Gradio layer:
    1. Input validation (length check via MAX_MESSAGE_LENGTH)
    2. Logging via existing LOGGER (utils/logger.py)

    Agent layer security (preserved):
    - LlamaFirewall semantic analysis (check_input_node)
    - llm-guard output sanitization (check_output_node)

    Rate limiting handled by Nginx proxy (per IP).
    """

    # ── Input Validation ────────────────────────────────────────────────────
    if not user_message or not user_message.strip():
        return ""

    if len(user_message) > MAX_MESSAGE_LENGTH:
        LOGGER.warning(
            "Message too long: %d > %d characters",
            len(user_message),
            MAX_MESSAGE_LENGTH,
        )
        return (
            f"Error: Message exceeds maximum length of {MAX_MESSAGE_LENGTH} characters"
        )

    # ── Log Request ─────────────────────────────────────────────────────────
    LOGGER.info("Gradio message: %.80s", user_message)

    try:
        result = await graph.ainvoke(
            {
                "messages": [HumanMessage(content=user_message)],
                "final_response": None,
                "error": None,
            }
        )
    except Exception as e:
        LOGGER.error("graph.ainvoke failed", exc_info=True)
        return f"Unexpected error: {e}"

    if result.get("error"):
        LOGGER.warning("Agent returned error: %s", result["error"])
        return f"Error: {result['error']}"

    response = result.get("final_response") or "No response generated."
    LOGGER.info("Gradio response: %.80s", response[:80] if response else "(empty)")

    return response


def create_demo():
    """Create Gradio demo — no auth field (Nginx Basic Auth handles authentication)."""
    with gr.Blocks(title="AI Assistant") as demo:
        gr.Markdown("## AI Assistant")
        gr.Markdown(
            "Ask your questions — the assistant can read files, search the web, "
            "and generate documents."
        )

        # No API key field — authentication handled by Nginx Basic Auth
        chatbot = gr.ChatInterface(
            fn=chat,
            examples=[
                "List files in the root directory",
                "Search for information about LangGraph on the web",
                "Write a test document in the 'output' folder",
            ],
        )

    return demo


demo = create_demo()

# Launch — Indique à Gradio qu'il fonctionne derrière le reverse proxy Nginx
demo.launch(server_name="0.0.0.0", server_port=7860)
