# utils/preprocessing.py
import re
import fitz
from docx import Document
from llm_guard import scan_prompt


def collapse_spaced_letters(text: str) -> str:
    """
    Collapses spaced-out uppercase letters into a single string to help PII scanners detect them.

    Example:
        Input: 'C H R I S T O P H E'
        Output: 'CHRISTOPHE'

    Args:
        text: Input string containing potentially spaced-out uppercase letters.

    Returns:
        str: Modified string with spaced-out letters collapsed.

    Implementation:
        Uses regex to find patterns of uppercase letters separated by whitespace and
        replaces them with their concatenated version.
    """
    return re.sub(
        r"\b([A-Z])(?:\s+([A-Z]))+\b", lambda m: re.sub(r"\s+", "", m.group(0)), text
    )
