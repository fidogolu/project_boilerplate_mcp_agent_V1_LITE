"""Async HTTP client for MCP endpoints.

Each MCP endpoint exposes a JSON-RPC interface over HTTP/HTTPS.

All MCP calls from agent tools must go through MCP_CLIENT.

Usage:
    from utils.mcp_client import MCP_CLIENT

    # Recommended: Use as context manager for proper cleanup
    async with MCP_CLIENT as client:
        content = await client.file_read("document.txt")

    # Or if using the singleton directly (ensure app shutdown handles cleanup)
    # content = await MCP_CLIENT.file_read("document.txt")
"""

import asyncio
import json
from typing import Optional

import httpx

from config.constants import MCP_BASE_URL


_MCP_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
}


def _build_jsonrpc(method: str, params: dict, req_id: int = 1) -> dict:
    """Build a JSON-RPC 2.0 request payload."""
    return {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": req_id,
    }


def _text(result: dict) -> str:
    """Extract text content from MCP tool result."""
    if not result:
        return ""
    content_list = result.get("content", [])
    if not content_list:
        return ""
    return content_list[0].get("text", "")


def _parse_sse(text: str) -> dict:
    """
    Parse Server-Sent Events (SSE) response.

    MCP responses are streamed. A single JSON-RPC response might be split across
    multiple 'data:' frames. This function handles fragmentation and extracts
    the final result.
    """
    lines = text.splitlines()
    current_data_parts = []

    for line in lines:
        if line.startswith("data:"):
            data_str = line[len("data:") :].strip()
            if not data_str:
                if current_data_parts:
                    try:
                        full_json = "".join(current_data_parts)
                        data = json.loads(full_json)

                        if "error" in data:
                            error_code = data["error"]["code"]
                            error_msg = data["error"]["message"]
                            raise RuntimeError(f"MCP error {error_code}: {error_msg}")
                        return data.get("result", {})
                    except json.JSONDecodeError as e:
                        raise RuntimeError(
                            f"Failed to parse SSE JSON fragment: {e}. Raw: {full_json}"
                        )
                    finally:
                        current_data_parts = []
            else:
                current_data_parts.append(data_str)

    if current_data_parts:
        try:
            full_json = "".join(current_data_parts)
            data = json.loads(full_json)
            return data.get("result", {})
        except json.JSONDecodeError:
            return {}

    return {}


class MCP_CLIENT:
    """Async HTTP client for MCP endpoints."""

    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None
        self._lock = asyncio.Lock()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, *args):
        await self.close()
        return False

    async def connect(self):
        """Create an HTTP client."""
        async with self._lock:
            if self._client and not self._client.is_closed:
                return

            self._client = httpx.AsyncClient(
                base_url=MCP_BASE_URL,
                headers=_MCP_HEADERS,
                timeout=httpx.Timeout(60.0, connect=10.0),
            )

    async def close(self):
        """Close the HTTP client."""
        async with self._lock:
            if self._client and not self._client.is_closed:
                await self._client.aclose()
                self._client = None

    async def _request(self, method: str, params: dict) -> dict:
        """Send a JSON-RPC request to an MCP endpoint."""
        if not self._client or self._client.is_closed:
            await self.connect()

        req_id = id(asyncio.current_task())
        payload = _build_jsonrpc(method, params, req_id)

        response = await self._client.post("/message", json=payload)
        response.raise_for_status()

        return _parse_sse(response.text)

    # ── File Management endpoints ─────────────────────────────────────────────

    async def file_read(self, relative_path: str) -> str:
        """Read a file from the file system."""
        result = await self._request("file_read", {"path": relative_path})
        return _text(result)

    async def file_list(self, relative_path: str = ".", recursive: bool = False) -> str:
        """List directory contents."""
        result = await self._request(
            "file_list", {"path": relative_path, "recursive": recursive}
        )
        return _text(result)

    async def file_search(self, pattern: str, relative_path: str = ".") -> str:
        """Search for files matching a pattern."""
        result = await self._request(
            "file_search", {"pattern": pattern, "path": relative_path}
        )
        return _text(result)

    # ── Web Search endpoints ──────────────────────────────────────────────────

    async def web_search(self, query: str, max_results: int = 10) -> str:
        """Search the web."""
        result = await self._request(
            "web_search", {"query": query, "max_results": max_results}
        )
        return _text(result)

    async def fetch_url(self, url: str) -> str:
        """Fetch a web page."""
        result = await self._request("fetch_url", {"url": url})
        return _text(result)

    # ── Document Writer endpoints ─────────────────────────────────────────────

    async def doc_write(
        self, directory: str, filename: str, content: str, mode: str = "write"
    ) -> str:
        """Write or append to a file."""
        result = await self._request(
            "doc_write",
            {
                "directory": directory,
                "filename": filename,
                "content": content,
                "mode": mode,
            },
        )
        return _text(result)

    async def doc_create_directory(self, directory: str, parents: bool = False) -> str:
        """Create a directory."""
        result = await self._request(
            "doc_create_directory",
            {"directory": directory, "parents": parents},
        )
        return _text(result)

    async def doc_rename(self, old_path: str, new_path: str) -> str:
        """Rename or move a file."""
        result = await self._request(
            "doc_rename", {"old_path": old_path, "new_path": new_path}
        )
        return _text(result)

    # ── Legacy aliases (for backward compatibility) ───────────────────────────

    async def obsidian_read(self, path: str) -> str:
        """Alias for file_read."""
        return await self.file_read(path)

    async def obsidian_list(self, path: str, recursive: bool = False) -> str:
        """Alias for file_list."""
        return await self.file_list(path, recursive)

    async def obsidian_search(self, pattern: str, path: str = ".") -> str:
        """Alias for file_search."""
        return await self.file_search(pattern, path)

    async def markdown_write(
        self, directory: str, filename: str, content: str, mode: str = "write"
    ) -> str:
        """Alias for doc_write."""
        return await self.doc_write(directory, filename, content, mode)

    async def markdown_create_directory(
        self, directory: str, parents: bool = False
    ) -> str:
        """Alias for doc_create_directory."""
        return await self.doc_create_directory(directory, parents)

    async def markdown_rename(self, old_path: str, new_path: str) -> str:
        """Alias for doc_rename."""
        return await self.doc_rename(old_path, new_path)

    @property
    async def get_client(self):
        """Return the connected client instance."""
        await self.connect()
        return self


# Singleton instance
MCP_CLIENT = MCP_CLIENT()
