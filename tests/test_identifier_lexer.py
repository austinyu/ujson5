"""Test the identifier lexer."""

from copy import copy
import pytest

from pyjp5.core import JSON5DecodeError
from pyjp5.lexer import (
    TokenType,
    tokenize_identifier,
)
from pyjp5.lexer_consts import (
    UNICODE_LETTERS,
    UNICODE_COMBINING_MARKS,
    UNICODE_DIGITS,
    UNICODE_CONNECTORS,
    ZWJ,
    ZWNJ,
)

unicode_letters = copy(UNICODE_LETTERS)
unicode_combining_marks = copy(UNICODE_COMBINING_MARKS)
unicode_digits = copy(UNICODE_DIGITS)
unicode_connectors = copy(UNICODE_CONNECTORS)


@pytest.mark.parametrize(
    "identifiers, start, end",
    [
        ("a", 0, 1),
        ("A", 0, 1),
        ("_A", 0, 2),
        ("$A", 0, 2),
        ("\\u00A9", 0, 6),
        ("a02a ", 0, 4),
        ("_\\u0312:   ", 0, 7),
        (f"{unicode_letters.pop()}{unicode_combining_marks.pop()}", 0, 2),
        (f"{unicode_letters.pop()}{ZWJ}{ZWNJ}", 0, 3),
        (f"{unicode_letters.pop()}{unicode_digits.pop()}", 0, 2),
        (f"{unicode_letters.pop()}{unicode_connectors.pop()}", 0, 2),
    ],
)
def test_valid_identifiers(identifiers: str, start: int, end: int) -> None:
    """Test valid identifiers."""
    result = tokenize_identifier(buffer=identifiers, idx=0)
    assert result.token is not None
    assert result.token.tk_type == TokenType.JSON5_IDENTIFIER
    r_start, r_end = result.token.value
    assert (r_start, r_end) == (start, end)


@pytest.mark.parametrize(
    "identifiers",
    [
        "\\u22\\xab",
        f"\\u{unicode_combining_marks.pop()}",
        f"{unicode_digits.pop()}",
        f"{unicode_connectors.pop()}",
        "A\u2603",  # invalid unicode escape sequence
    ],
)
def test_invalid_identifiers(identifiers: str) -> None:
    """Test invalid identifiers."""
    with pytest.raises(JSON5DecodeError):
        tokenize_identifier(buffer=identifiers, idx=0)
