# agents/tools.py
"""LangGraph tools — wrap MCP_CLIENT calls for use in the ReAct agent.

Each tool applies check_input / check_output around the MCP call.
Never call MCP_CLIENT directly from graph.py or nodes — use these tools.
"""

from langchain_core.tools import tool

from utils.logger import LOGGER
from utils.mcp_client import MCP_CLIENT
from utils.security import check_input, check_output


def _block_error(reason: str) -> str:
    return f"[BLOCKED] {reason}"


# ── File Management Tools ─────────────────────────────────────────────────────


@tool
async def read_file(relative_path: str) -> str:
    """Read the content of a file from the file system.

    Args:
        relative_path: Relative path to the file (e.g. 'documents/report.txt').
    """
    safe = check_input(relative_path)
    if safe.is_blocked:
        return _block_error(safe.reason)
    try:
        # 1. Get the MCP client
        client = await MCP_CLIENT.get_client()
        # 2. Call the MCP method
        result = await client.file_read(safe.sanitized_text)
        safe_out = check_output(result)
        if safe_out.is_blocked:
            return _block_error(safe_out.reason)
        return safe_out.sanitized_text
    except Exception as e:
        LOGGER.error("read_file failed", exc_info=True)
        return f"Error: {e}"


@tool
async def list_directory(relative_path: str = ".", recursive: bool = False) -> str:
    """List the contents of a directory.

    Args:
        relative_path: Relative path to the directory (default: root '.').
        recursive: Whether to list recursively.
    """
    safe = check_input(relative_path)
    if safe.is_blocked:
        return _block_error(safe.reason)
    try:
        # 1. Get the MCP client
        client = await MCP_CLIENT.get_client()
        # 2. Call the MCP method
        result = await client.file_list(safe.sanitized_text, recursive)
        safe_out = check_output(result)
        if safe_out.is_blocked:
            return _block_error(safe_out.reason)
        return safe_out.sanitized_text
    except Exception as e:
        LOGGER.error("list_directory failed", exc_info=True)
        return f"Error: {e}"


@tool
async def search_files(pattern: str, relative_path: str = ".") -> str:
    """Search for files matching a pattern in the file system.

    Args:
        pattern: Glob or regex pattern to search for (e.g. '*.txt', 'report').
        relative_path: Directory to search in (default: root '.').
    """
    safe = check_input(pattern)
    if safe.is_blocked:
        return _block_error(safe.reason)
    try:
        # 1. Get the MCP client
        client = await MCP_CLIENT.get_client()
        # 2. Call the MCP method
        result = await client.file_search(safe.sanitized_text, relative_path)
        safe_out = check_output(result)
        if safe_out.is_blocked:
            return _block_error(safe_out.reason)
        return safe_out.sanitized_text
    except Exception as e:
        LOGGER.error("search_files failed", exc_info=True)
        return f"Error: {e}"


# ── Web Search tools ──────────────────────────────────────────────────────────


@tool
async def search_web(query: str, max_results: int = 10) -> str:
    """Search the web and return structured results.

    Args:
        query: Search query string.
        max_results: Number of results to return (1-50, default 10).
    """
    safe = check_input(query)
    if safe.is_blocked:
        return _block_error(safe.reason)
    try:
        # 1. Get the MCP client
        client = await MCP_CLIENT.get_client()
        # 2. Call the MCP method
        result = await client.web_search(safe.sanitized_text, max_results)
        safe_out = check_output(result)
        if safe_out.is_blocked:
            return _block_error(safe_out.reason)
        return safe_out.sanitized_text
    except Exception as e:
        LOGGER.error("search_web failed", exc_info=True)
        return f"Error: {e}"


@tool
async def fetch_url(url: str) -> str:
    """Fetch the text content of a web page.

    Args:
        url: Full HTTP/HTTPS URL to fetch.
    """
    safe = check_input(url)
    if safe.is_blocked:
        return _block_error(safe.reason)
    try:
        # 1. Get the MCP client
        client = await MCP_CLIENT.get_client()
        # 2. Call the MCP method
        result = await client.fetch_url(safe.sanitized_text)
        safe_out = check_output(result)
        if safe_out.is_blocked:
            return _block_error(safe_out.reason)
        return safe_out.sanitized_text
    except Exception as e:
        LOGGER.error("fetch_url failed", exc_info=True)
        return f"Error: {e}"


# ── Document Writer tools ─────────────────────────────────────────────────────


@tool
async def write_file(
    directory: str, filename: str, content: str, mode: str = "write"
) -> str:
    """Write or append content to a file.

    Args:
        directory: Target directory (e.g. 'documents').
        filename: Output filename (e.g. 'summary.txt').
        content: Content to write.
        mode: 'write' (overwrite) or 'append' (add to end).
    """
    safe = check_input(content)
    if safe.is_blocked:
        return _block_error(safe.reason)
    try:
        # 1. Get the MCP client
        client = await MCP_CLIENT.get_client()
        # 2. Call the MCP method
        result = await client.doc_write(directory, filename, safe.sanitized_text, mode)
        return result
    except Exception as e:
        LOGGER.error("write_file failed", exc_info=True)
        return f"Error: {e}"


@tool
async def create_directory(directory: str, parents: bool = False) -> str:
    """Create a directory.

    Args:
        directory: Directory path.
        parents: Create parent directories if needed.
    """
    safe = check_input(directory)
    if safe.is_blocked:
        return _block_error(safe.reason)
    try:
        # 1. Get the MCP client
        client = await MCP_CLIENT.get_client()
        # 2. Call the MCP method
        result = await client.doc_create_directory(directory, parents)
        safe_out = check_output(result)
        if safe_out.is_blocked:
            return _block_error(safe_out.reason)
        return safe_out.sanitized_text
    except Exception as e:
        LOGGER.error("create_directory failed", exc_info=True)
        return f"Error: {e}"


@tool
async def rename_file(old_path: str, new_path: str) -> str:
    """Rename or move a file.

    Args:
        old_path: Current path of the file.
        new_path: New path for the file.
    """
    safe = check_input(old_path + " " + new_path)
    if safe.is_blocked:
        return _block_error(safe.reason)
    try:
        # 1. Get the MCP client
        client = await MCP_CLIENT.get_client()
        # 2. Call the MCP method
        result = await client.doc_rename(old_path, new_path)
        safe_out = check_output(result)
        if safe_out.is_blocked:
            return _block_error(safe_out.reason)
        return safe_out.sanitized_text
    except Exception as e:
        LOGGER.error("rename_file failed", exc_info=True)
        return f"Error: {e}"


# ── Tool registry ─────────────────────────────────────────────────────────────
TOOLS = [
    read_file,
    list_directory,
    search_files,
    search_web,
    fetch_url,
    write_file,
    create_directory,
    rename_file,
]
