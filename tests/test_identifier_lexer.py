"""Test the identifier lexer."""

from copy import copy
from random import choice, randint, sample
import pytest

from ujson5.core import JSON5DecodeError, TOKEN_TYPE
from ujson5.lexer import (
    tokenize_identifier,
)
from ujson5.consts import (
    UNICODE_LETTERS,
    UNICODE_COMBINING_MARKS,
    UNICODE_DIGITS,
    UNICODE_CONNECTORS,
    ZWJ,
    ZWNJ,
    PUNCTUATORS,
)

unicode_letters = copy(UNICODE_LETTERS)
unicode_combining_marks = copy(UNICODE_COMBINING_MARKS)
unicode_digits = copy(UNICODE_DIGITS)
unicode_connectors = copy(UNICODE_CONNECTORS)

VALID_HEX_DIGITS = "0123456789abcdefABCDEF"
RANDOM_UNICODE_ESCAPE = (
    f"\\u{choice(VALID_HEX_DIGITS)}{choice(VALID_HEX_DIGITS)}"
    f"{choice(VALID_HEX_DIGITS)}{choice(VALID_HEX_DIGITS)}"
)


@pytest.mark.parametrize(
    "identifier, start, end",
    [
        ("a", 0, 1),
        ("A", 0, 1),
        ("_A", 0, 2),
        ("$A", 0, 2),
        (RANDOM_UNICODE_ESCAPE, 0, 6),
        (f"a02a{' ' * randint(0, 10)}", 0, 4),
        *[(f"_\\u0312{p}   ", 0, 7) for p in PUNCTUATORS],
        (f"{unicode_letters.pop()}{unicode_combining_marks.pop()}", 0, 2),
        (f"{unicode_letters.pop()}{ZWJ}{ZWNJ}", 0, 3),
        (f"{unicode_letters.pop()}{unicode_digits.pop()}", 0, 2),
        (f"{unicode_letters.pop()}{unicode_connectors.pop()}", 0, 2),
    ],
)
def test_valid_identifiers(identifier: str, start: int, end: int) -> None:
    """Test valid identifiers."""
    result = tokenize_identifier(buffer=identifier, idx=0)
    assert result.token is not None
    assert result.token.tk_type == TOKEN_TYPE["IDENTIFIER"]
    r_start, r_end = result.token.value
    assert (r_start, r_end) == (start, end)


@pytest.mark.parametrize(
    "identifier",
    [
        "\\u22\\xab",
        "\\u",
        *sample(list(unicode_combining_marks), k=min(10, len(unicode_combining_marks))),
        *sample(list(unicode_digits), k=min(10, len(unicode_digits))),
        *sample(list(unicode_connectors), k=min(10, len(unicode_connectors))),
        "A\u2603",  # invalid unicode escape sequence
    ],
)
def test_invalid_identifiers(identifier: str) -> None:
    """Test invalid identifiers."""
    with pytest.raises(JSON5DecodeError):
        tokenize_identifier(buffer=identifier, idx=0)
