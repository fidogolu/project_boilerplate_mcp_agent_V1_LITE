# config/constants.py
"""All URLs, model names, paths, and constants — single source of truth.

Never use os.getenv() directly outside this file.
"""

import os

from dotenv import load_dotenv

load_dotenv()

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# ── LLM endpoint ─────────────────────────────────────────────────────────────
WORKER_LLM_URL = os.getenv("WORKER_LLM_URL", "http://localhost:10001/v1")
WORKER_MODEL_NAME = os.getenv("WORKER_MODEL_NAME", "llm-model-name")

# ── MCP endpoint ─────────────────────────────────────────────────────────────
MCP_BASE_URL = os.getenv("MCP_BASE_URL", "https://mcp.example.com")

# ── Security ──────────────────────────────────────────────────────────────────
SECURITY_MODE = os.getenv(
    "SECURITY_MODE", "llamafirewall"
)  # lite | full | remote | llamafirewall
SECURITY_SERVICE_URL = os.getenv("SECURITY_SERVICE_URL", "")

# LlamaFirewall configuration
LLAMAFIREWALL_TIMEOUT = int(os.getenv("LLAMAFIREWALL_TIMEOUT", "30"))
LLAMAFIREWALL_THRESHOLD = float(os.getenv("LLAMAFIREWALL_THRESHOLD", "0.5"))
LLAMAFIREWALL_INPUT_THRESHOLD = float(os.getenv("LLAMAFIREWALL_INPUT_THRESHOLD", "0.6"))
LLAMAFIREWALL_OUTPUT_THRESHOLD = float(
    os.getenv("LLAMAFIREWALL_OUTPUT_THRESHOLD", "0.6")
)

# Security bypass — list of categories to skip (comma-separated, empty = block all)
SECURITY_BYPASS_CATEGORIES = os.getenv("SECURITY_BYPASS_CATEGORIES", "").strip()

# ── Observability ─────────────────────────────────────────────────────────────
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "http://localhost:3000")
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY", "")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY", "")

# ── Gradio ────────────────────────────────────────────────────────────────────
GRADIO_TEMP_DIR = os.getenv("GRADIO_TEMP_DIR", "./temp_data")
MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", "4096"))
MAX_CONVERSATION_HISTORY = int(os.getenv("MAX_CONVERSATION_HISTORY", "50"))
