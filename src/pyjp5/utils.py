"""Utility functions."""

import re

from .lexer_consts import ESCAPE_SEQUENCE


def simplify_escapes(string: str) -> str:
    """Simplify escape sequences in a string. This function replaces line
    continuation sequences with a newline character.

    Args:
        string (str): string with escape sequences

    Returns:
        str: string with escape sequences simplified
    """
    string = re.sub(
        r"(?:\u000D\u000A|[\u000A\u000D\u2028\u2029])",
        "\n",
        string,
    )
    return string


def unescape_escaped_sequence(s: str) -> str:
    """Unescape escape sequences in a string."""

    return re.sub(
        r"\\([\'\"\\bfnrtv0])",
        lambda match: ESCAPE_SEQUENCE[str(match.group(1))],
        s,
    )


def unescape_line_continuation(s: str) -> str:
    """Unescape line continuation in a string."""
    return re.sub(r"\\\s*\n", "\n", s)
