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
    return re.sub(r"\\\s*\n", "\n", text)
