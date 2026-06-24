# 🛡️ Secure Agent Boilerplate

> A production-ready boilerplate for building secured AI agents with ReAct loop orchestration via LangGraph and multi-layer security scanning.

---

## 📌 Description

**Secure Agent Boilerplate** is a modular AI agent framework designed as a reusable template for building **production-grade, secure AI applications**. It demonstrates a complete architecture stack including:

- **ReAct Agent Loop** orchestrated by LangGraph with built-in security gates
- **Multi-layer security scanning** for prompt injection, toxicity, and bias detection
- **MCP (Model Context Protocol)** integration for external tool calling
- **Modular architecture** with clear separation of concerns

This boilerplate is technology-agnostic and designed to be adapted to any MCP endpoint or external tool-calling service.

---

## ✨ Key Features

### Architecture & Patterns

| Feature | Description |
|---------|-------------|
| **Clean Architecture** | Separation of concerns between agents, tools, utilities, and configuration layers |
| **ReAct Pattern** | LangGraph-based state machine implementing the Reason-Act loop |
| **Singleton Pattern** | Thread-safe singleton for LLM worker and MCP client |
| **Strategy Pattern** | Pluggable security modes (`lite`, `full`, `remote`, `llamafirewall`) |
| **Context Manager** | Async context manager for MCP client lifecycle |

### Security

| Feature | Description |
|---------|-------------|
| **Prompt Injection Detection** | LlamaFirewall semantic analysis + llm-guard |
| **Toxicity/Bias Scanning** | Multi-model output validation |
| **Input/Output Sanitization** | Automatic sanitization with configurable thresholds |
| **Configurable Security Modes** | Switch between lite, full, remote, or llamafirewall modes |

### Developer Experience

| Feature | Description |
|---------|-------------|
| **Strict Types** | Python TypedDict + Annotated types for state management |
| **Structured Logging** | Production-ready logger with file and console handlers |
| **Configuration Management** | Single source of truth via `config/constants.py` |
| **uv Package Management** | Fast, dependency-resolved Python environment |

---

## 🧠 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface                          │
│                  (Gradio Chat Interface)                     │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│              Agent Orchestration                             │
│           (LangGraph ReAct Loop)                             │
│  ┌──────────┐  ┌──────┐  ┌─────┐  ┌──────────┐            │
│  │check_input│→│call_llm│→│tools│→│check_output│           │
│  └──────────┘  └──────┘  └─────┘  └──────────┘            │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                  Security Layer                              │
│   (LlamaFirewall + llm-guard: Injection, Toxicity, Bias)   │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│              MCP Client (HTTP)                               │
│    ┌────────────┐ ┌─────────────┐ ┌──────────────┐         │
│    │/endpoint-a │ │/endpoint-b  │ │/endpoint-c    │         │
│    └────────────┘ └─────────────┘ └──────────────┘         │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│            MCP Endpoints (Remote)                            │
│              mcp.example.com                                 │
└─────────────────────────────────────────────────────────────┘
```

### Technical Stack

| Category | Technology |
|----------|-----------|
| **Agent Framework** | LangGraph, LangChain |
| **MCP Protocol** | httpx (async, HTTP/2) |
| **Security** | LlamaFirewall, llm-guard |
| **LLM Inference** | llama.cpp (OpenAI-compatible API) |
| **GPU Acceleration** | PyTorch (CUDA 12.8+), torchvision |
| **UI** | Gradio |
| **Observability** | Langfuse |
| **Configuration** | python-dotenv, uv |

---

## 📁 Project Structure

```
secure-agent-boilerplate/
├── main.py                    # Entry point (Gradio UI + agent logic)
├── pyproject.toml             # Dependencies & uv configuration
├── .env.example               # Template configuration
├── README.md                  # This file
├── LICENSE.md                 # MIT License
│
├── agents/                    # Agent core components
│   ├── graph.py               # LangGraph ReAct loop definition
│   ├── state.py               # AgentState TypedDict
│   └── tools.py               # MCP tool wrappers
│
├── config/                    # Configuration layer
│   └── constants.py           # Single source of truth
│
├── utils/                     # Utility modules
│   ├── llm.py                 # LLM worker singleton
│   ├── logger.py              # Logging configuration
│   ├── mcp_client.py          # Async HTTP client
│   └── security.py            # Security scanners
│
├── tests/                     # Test suite
│   └── test_security.py
│
└── docs/
    ├── architecture.mermaid   # Architecture diagram
    └── README_CODE.md         # Technical documentation
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- uv (Python package manager): `pip install uv`

### Local Development

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/secure-agent-boilerplate.git
cd secure-agent-boilerplate

# 2. Create a virtual environment with uv
uv sync

# 3. Copy and configure environment variables
cp .env.example .env
# Edit .env with your LLM endpoint, MCP URLs, and security settings

# 4. Run the agent
uv run python main.py
```

---

## 🧪 Testing

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run security tests only
uv run pytest tests/test_security.py -v
```

---

## 📝 Configuration

All configuration is managed through environment variables. See [`.env.example`](.env.example) for the full list.

### Key Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `WORKER_LLM_URL` | LLM API endpoint | `http://localhost:10001/v1` |
| `WORKER_MODEL_NAME` | Model to use | `llm-model-name` |
| `MCP_BASE_URL` | MCP endpoint base URL | `https://mcp.example.com` |
| `SECURITY_MODE` | Security scanning mode | `llamafirewall` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |

### Security Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `lite` | Basic scanners, no GPU required | Development |
| `full` | All scanners + GPU models | Production (single-host) |
| `remote` | HTTP call to security service | Production (multi-host) |
| `llamafirewall` | Semantic analysis + llm-guard | **Recommended** |

---

## 🏗️ Architecture Deep Dive

### ReAct Loop

The agent follows the **ReAct (Reason + Act)** pattern:

```
User Input → [Security Check] → LLM Call → Tool Execution? → [Security Check] → Response
                    ↓                    ↓                    ↓                  ↓
              Input validation     Tool selection      Output sanitization    Final answer
```

Each node in the graph is independently testable and the security gates are applied at both input and output boundaries.

### Security Strategy

The security layer follows a **defense-in-depth** approach:

1. **Layer 1 — Input Validation**: Message length limits, format validation
2. **Layer 2 — Semantic Analysis**: LlamaFirewall detects prompt injection attempts
3. **Layer 3 — Token-level Scanning**: llm-guard checks for toxicity, bias, sensitive data
4. **Layer 4 — Output Sanitization**: All LLM outputs are scanned before delivery

### MCP Client

The MCP client provides a clean abstraction over HTTP-based MCP endpoints:

```python
from utils.mcp_client import MCP_CLIENT

# Use as context manager
async with MCP_CLIENT as client:
    content = await client.file_read("document.txt")

# Or use the singleton
result = await MCP_CLIENT.file_read("document.txt")
```

---

## 📄 License

MIT License — see [`LICENSE.md`](LICENSE.md)

---

## 🤝 Contributing

This is a boilerplate template. Feel free to fork, adapt, and use as a starting point for your own secure AI agent projects.

### When forking, consider:

- Updating the `.env.example` with your own defaults
- Adapting tool wrappers to your MCP endpoints
- Adding your own security scanners

---

*Built with LangGraph, httpx, and Gradio. Designed for production.*
