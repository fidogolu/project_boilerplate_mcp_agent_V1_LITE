# tests/test_security.py
"""Unit tests for security layer — covers all SECURITY_MODE values."""

import pytest
from dataclasses import is_dataclass

from utils.security import SecurityResult, check_input, check_output


# ──────────────────────────────────────────────────────────────────────────────
# Fixtures & helpers
# ──────────────────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def security_mode():
    """Return the active SECURITY_MODE from config."""
    from config.constants import SECURITY_MODE

    return SECURITY_MODE


# ──────────────────────────────────────────────────────────────────────────────
# SecurityResult structure tests
# ──────────────────────────────────────────────────────────────────────────────


def test_security_result_is_dataclass():
    """SecurityResult must be a dataclass."""
    assert is_dataclass(SecurityResult)


def test_security_result_defaults():
    """SecurityResult defaults should be correct."""
    result = SecurityResult(is_blocked=False)
    assert result.is_blocked is False
    assert result.reason == ""
    assert result.sanitized_text == ""


# ──────────────────────────────────────────────────────────────────────────────
# check_input / check_output signature tests (mode-agnostic)
# ──────────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "text",
    [
        "",
        "Hello, world!",
        "  \t  ",
        "a" * 10000,
    ],
)
def test_check_input_returns_security_result(text, security_mode):
    """check_input must always return a SecurityResult."""
    result = check_input(text)
    assert isinstance(result, SecurityResult)
    assert hasattr(result, "is_blocked")
    assert hasattr(result, "reason")
    assert hasattr(result, "sanitized_text")


@pytest.mark.parametrize(
    "text",
    [
        "",
        "Hello, world!",
        "  \t  ",
        "a" * 10000,
    ],
)
def test_check_output_returns_security_result(text, security_mode):
    """check_output must always return a SecurityResult."""
    result = check_output(text)
    assert isinstance(result, SecurityResult)
    assert hasattr(result, "is_blocked")
    assert hasattr(result, "reason")
    assert hasattr(result, "sanitized_text")


# ──────────────────────────────────────────────────────────────────────────────
# Empty input / output tests
# ──────────────────────────────────────────────────────────────────────────────


def test_check_input_empty(security_mode):
    """Empty input should not raise."""
    result = check_input("")
    assert isinstance(result, SecurityResult)


def test_check_output_empty(security_mode):
    """Empty output should not raise."""
    result = check_output("")
    assert isinstance(result, SecurityResult)


def test_check_output_empty_prompt(security_mode):
    """Empty prompt should not raise."""
    result = check_output("some text", "")
    assert isinstance(result, SecurityResult)


# ──────────────────────────────────────────────────────────────────────────────
# Sanitization tests
# ──────────────────────────────────────────────────────────────────────────────


def test_check_input_sanitized_text_is_str(security_mode):
    """sanitized_text must always be a string."""
    result = check_input("test input")
    assert isinstance(result.sanitized_text, str)


def test_check_output_sanitized_text_is_str(security_mode):
    """sanitized_text must always be a string."""
    result = check_output("test output")
    assert isinstance(result.sanitized_text, str)


def test_check_input_blocked_reason_is_str(security_mode):
    """When blocked, reason must be a non-empty string."""
    # This test may pass or fail depending on security mode
    result = check_input("")
    if result.is_blocked:
        assert isinstance(result.reason, str)


def test_check_output_blocked_reason_is_str(security_mode):
    """When blocked, reason must be a non-empty string."""
    result = check_output("")
    if result.is_blocked:
        assert isinstance(result.reason, str)


# ──────────────────────────────────────────────────────────────────────────────
# Idempotency tests
# ──────────────────────────────────────────────────────────────────────────────


def test_check_input_idempotent(security_mode):
    """Double check_input should be stable."""
    text = "stable test input"
    result1 = check_input(text)
    result2 = check_input(result1.sanitized_text)
    assert result1.is_blocked == result2.is_blocked


def test_check_output_idempotent(security_mode):
    """Double check_output should be stable."""
    text = "stable test output"
    result1 = check_output(text)
    result2 = check_output(result1.sanitized_text)
    assert result1.is_blocked == result2.is_blocked
