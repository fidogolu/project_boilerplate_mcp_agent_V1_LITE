# utils/llm.py
"""WORKER_LLM singleton.

Import:
    from utils.llm import WORKER_LLM
"""

import httpx
from langchain_openai import ChatOpenAI

from config.constants import WORKER_LLM_URL, WORKER_MODEL_NAME

http_client = httpx.Client()
http_async_client = httpx.AsyncClient()

WORKER_LLM = ChatOpenAI(
    base_url=WORKER_LLM_URL,
    model=WORKER_MODEL_NAME,
    api_key="not-required",
    temperature=0.0,
    http_client=http_client,
    http_async_client=http_async_client,
)
