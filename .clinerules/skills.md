# Project Skills & Standards

## Stack
- **Language**: Python 3.10+
- **Framework**: LangGraph (ReAct agent) + Gradio 6 (chat UI) + uv (package manager)
- **LLM**: Nemotron-Nano-9B-v2 via llama.cpp (host :10001)
- **Security layer 1**: LlamaFirewall / PromptGuard2 — prompt injection detection on user input
- **Security layer 2**: llm-guard — input/output sanitisation in tools and nodes
- **MCP client**: httpx async + mTLS (3 client certs, one per MCP endpoint)
- **Observability**: Langfuse (existing container, accessed via host.docker.internal:3000)


## Security Modes (`SECURITY_MODE` env var)

| Mode | llm-guard | LlamaFirewall | Use case |
|------|-----------|---------------|----------|
| `lite` | Lightweight scanners (no torch) | Local, no torch | Development |
| `full` | All scanners + torch models | Local, with torch | Staging / prod |
| `remote` | HTTP call to `security` container | HTTP call | Production multi-host |

Switching modes = changing `SECURITY_MODE` in `.env` only. Zero new development.


## Architecture (source of truth)

```
Gradio chat
    → check_input (LlamaFirewall — prompt injection)
    → LangGraph ReAct agent (WORKER_LLM + tools)
        → tool: check_input (llm-guard) → MCP_CLIENT → check_output (llm-guard)
    → check_output (llm-guard)
    → Gradio response
```

No supervisor. No multi-agent routing. Single ReAct agent with MCP tools.


## MCP Backend Contract (source of truth — see mcp-backend-contract.md)

| Endpoint       | Route          | Cert required              | CN              |
|----------------|----------------|----------------------------|-----------------|
| Obsidian Read  | `/obsidian/`   | `agent_lecture.crt/.key`   | `agent-lecture` |
| Web Search     | `/web-search/` | `agent_analyse.crt/.key`   | `agent-analyse` |
| Markdown Write | `/markdown/`   | `agent_publication.crt/.key` | `agent-publication` |

- Protocol: HTTPS mTLS (`ssl_cert_reqs=CERT_REQUIRED`)
- Host: `https://mcp.mondomaine.com` (resolved via `extra_hosts` in docker-compose)
- Certs injected via Docker secrets into `/run/secrets/`
- Rate limit: 10 req/s — never call MCP in tight loops


## Project Structure (source of truth)

```
project/
├── main.py                    — Gradio 6 chat entry point
├── config/
│   └── constants.py           — ALL URLs, cert paths, model names, SECURITY_MODE
├── agent/
│   ├── state.py               — AgentState TypedDict
│   ├── graph.py               — LangGraph ReAct graph + conditional edges
│   └── tools.py               — @tool functions wrapping MCP_CLIENT
├── utils/
│   ├── logger.py              — LOGGER singleton
│   ├── llm.py                 — WORKER_LLM singleton
│   ├── security.py            — check_input() / check_output() (mode-aware)
│   └── mcp_client.py          — MCP_CLIENT singleton (3 httpx clients)
├── tests/
│   └── test_agent.py
├── Dockerfile
├── docker-compose.yml
└── .env
```


## Naming Conventions
- **Tools**: verb_noun (e.g. `read_vault_file`, `search_web`, `write_markdown_file`)
- **Nodes**: verb_noun (e.g. `check_input_node`, `call_llm`, `check_output_node`)
- **State keys**: snake_case, never abbreviated
- **Files**: snake_case strict
- **Private singletons**: prefix `_` (e.g. `_input_scanners`, `_promptguard`)
- **Public singletons**: UPPER_SNAKE_CASE (e.g. `LOGGER`, `WORKER_LLM`, `MCP_CLIENT`)
- **Constants**: UPPER_SNAKE_CASE in `config/constants.py` only


## Agent State (`agent/state.py`)

```python
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    final_response: Optional[str]
    error: Optional[str]
```

Never add keys without Architect approval. Never create a second state TypedDict.


## LangGraph Rules
- A node returns ONLY the keys it modifies (LangGraph merges state automatically)
- Never use `{**state, ...}` unless explicitly resetting multiple keys (must be commented)
- Always check `state.get("error")` at the start of every node — short-circuit if set
- Conditional edges in `agent/graph.py` only — never inside nodes or tools
- `ToolNode` from `langgraph.prebuilt` handles tool execution — never call tools manually


## Tools (`agent/tools.py`)
- Each tool wraps exactly one MCP operation
- Every tool applies `check_input` on arguments and `check_output` on the MCP result
- Tools never call httpx directly — always via `MCP_CLIENT`
- Tool docstrings are shown to the LLM — be explicit and precise
- All tools registered in `TOOLS` list at the bottom of the file


## MCP Client (`utils/mcp_client.py`)
- `MCP_CLIENT` is the only entry point for all MCP calls
- Three internal httpx clients, one per endpoint (each with its own cert pair)
- Never import httpx directly in tools or nodes

```python
from utils.mcp_client import MCP_CLIENT

await MCP_CLIENT.obsidian_read(relative_path)     # uses agent_lecture cert
await MCP_CLIENT.web_search(query)                 # uses agent_analyse cert
await MCP_CLIENT.markdown_write(dir, file, content) # uses agent_publication cert
```


## Security (`utils/security.py`)

```python
from utils.security import check_input, check_output

safe = check_input(text)
if safe.is_blocked:
    return {"error": f"Input blocked: {safe.reason}"}

safe = check_output(text)
if safe.is_blocked:
    return {"error": f"Output blocked: {safe.reason}"}
```

Checkpoints:
- User message → `check_input` (LlamaFirewall) in `check_input_node`
- Tool argument → `check_input` (llm-guard) in each `@tool`
- MCP result → `check_output` (llm-guard) in each `@tool`
- Agent response → `check_output` (llm-guard) in `check_output_node`


## LLM (`utils/llm.py`)

```python
from utils.llm import WORKER_LLM
```

- Only one LLM singleton — `WORKER_LLM`
- Never instantiate `ChatOpenAI` outside `utils/llm.py`
- Never hardcode URLs or model names — `config/constants.py` only
- LLM accessed via `host.docker.internal:10001` from inside containers


## Logger (`utils/logger.py`)

```python
from utils.logger import LOGGER

LOGGER.info("message")
LOGGER.warning("message")
LOGGER.error("message", exc_info=True)
LOGGER.debug("message")
```

- Always use `LOGGER` — never `logging.getLogger()` directly
- Log level controlled by `LOG_LEVEL` env var (default: INFO)


## Config (`config/constants.py`)
All of the following must live here — never hardcoded elsewhere:

```python
WORKER_LLM_URL            # llama.cpp on host
WORKER_MODEL_NAME
MCP_BASE_URL              # https://mcp.mondomaine.com
SECURITY_MODE             # lite | full | remote
MCP_CA_CERT               # /run/secrets/mcp_ca_crt
AGENT_LECTURE_CERT/KEY    # /run/secrets/agent_lecture_crt/.key
AGENT_ANALYSE_CERT/KEY    # /run/secrets/agent_analyse_crt/.key
AGENT_PUBLICATION_CERT/KEY # /run/secrets/agent_publication_crt/.key
LANGFUSE_HOST             # http://host.docker.internal:3000
```


## Gradio (`main.py`)
- Single `gr.ChatInterface` — no file upload, no complex layout
- Early-return validation: empty message → return immediately, never invoke graph
- Final result always from `result.get("final_response")`
- Never call tools or MCP directly from `main.py`


## Tests (`tests/`)
- `WORKER_LLM` must be mocked — never load real models
- `MCP_CLIENT` must be mocked — never make real MCP calls
- Security scanners must be mocked
- Use `pytest-asyncio` with `asyncio_mode = "auto"`


## LangChain Imports (canonical)
```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
```
Never import from `langchain.schema`, `langchain.embeddings`, `langchain.vectorstores` (deprecated).


## Never
- No `print()` — always `LOGGER`
- No hardcoded URLs, model names, or paths — `config/constants.py` only
- No `ChatOpenAI` instantiation outside `utils/llm.py`
- No raw httpx calls in tools — `MCP_CLIENT` only
- No tool that skips `check_input` / `check_output`
- No singleton initialized inside a function or node
- No conditional edges inside nodes or tools — `agent/graph.py` only
- No supervisor, no multi-agent routing — ReAct agent only
- No user input reaching LLM without `check_input()` first
- No LLM output reaching Gradio without `check_output()` first
