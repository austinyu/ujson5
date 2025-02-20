"""Utility functions."""

import re

from .lexer_consts import ESCAPE_SEQUENCE


def simplify_escapes(text: str) -> str:
    """Simplify escape sequences in a string. This function replaces line
    continuation sequences with a newline character.

    Args:
        text (str): string with escape sequences

    Returns:
        str: string with escape sequences simplified
    """
    return re.sub(
        r"(?:\u000D\u000A|[\u000A\u000D\u2028\u2029])",
        "\n",
        text,
    )


def unescape_escaped_sequence(text: str) -> str:
    """Unescape escape sequences in a string."""

    return re.sub(
        r"\\([\'\"\\bfnrtv0])",
        lambda match: ESCAPE_SEQUENCE[str(match.group(1))],
        text,
    )


def unescape_line_continuation(text: str) -> str:
    """Unescape line continuation in a string."""
    return re.sub(r"\\\s*\n", "", text)


def validate_line_continuation(text: str) -> bool:
    """Validate line continuation in a string. Line continuation is a `\\`
    followed by a newline character. This function returns True if `\\` is followed by
    any number of space and a new line. Otherwise, if `\\` is followed by at least one
    space and any character other than a newline, it returns False.

    Args:
        text (str): string to validate

    Returns:
        bool: True if line continuation is valid, False otherwise
    """
    if "\\" not in text:
        return True
    candidates = re.finditer(r"\\\s+[^\n]", text)
    for match in candidates:
        if not bool(re.search(r"\\\s*\n", match.group())):
            return False
    return True
