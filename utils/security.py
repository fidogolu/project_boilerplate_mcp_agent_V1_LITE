# utils/security.py
"""Security layer stub — boilerplate template.

In production, replace this stub with your own security implementation.
This module provides placeholder functions for check_input() and check_output()
that pass through all content without modification.

Usage:
    from utils.security import check_input, check_output
"""

from dataclasses import dataclass


@dataclass
class SecurityResult:
    """Result of a security check."""

    is_blocked: bool
    reason: str = ""
    sanitized_text: str = ""


def check_input(text: str, source: str = "unknown") -> SecurityResult:
    """Check input for security issues.

    Boilerplate stub — always passes through.
    Replace with your own implementation (llm-guard, LlamaFirewall, etc.).
    """
    return SecurityResult(is_blocked=False, sanitized_text=text)


def check_output(
    text: str, prompt: str = "", source: str = "unknown"
) -> SecurityResult:
    """Check output for security issues.

    Boilerplate stub — always passes through.
    Replace with your own implementation (llm-guard, LlamaFirewall, etc.).
    """
    return SecurityResult(is_blocked=False, sanitized_text=text)
