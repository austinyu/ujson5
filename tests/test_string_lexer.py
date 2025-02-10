"""Test the string lexer."""

from random import choice, choices, randint

import pytest

from pyjson5.core import JSON5DecodeError
from pyjson5.lexer import (
    ESCAPE_SEQUENCE,
    LINE_TERMINATOR_SEQUENCE,
    TokenType,
    simplify_escapes,
    tokenize_string,
)

ESCAPE_SEQUENCE_NO_NL = ESCAPE_SEQUENCE.copy()
del ESCAPE_SEQUENCE_NO_NL["n"]
del ESCAPE_SEQUENCE_NO_NL["r"]

string_valid_examples_raw: list[str] = [
    "",
    "",
    "0",
    "[\\',]",
    "{}",
    *[f"hello\\{es} with es" for es in ESCAPE_SEQUENCE_NO_NL],
]

string_valid_examples_single: list[str] = [
    f"'{raw}'{' ' * randint(1, 10)}{choice(list(LINE_TERMINATOR_SEQUENCE))}"
    for raw in string_valid_examples_raw
]

string_valid_examples_double: list[str] = [
    f'"{raw}"{" " * randint(1, 10)}{choice(list(LINE_TERMINATOR_SEQUENCE))}'
    for raw in string_valid_examples_raw
]

string_multi_lines_ext: list[tuple[list[str], int]] = [
    (["hello", " world"], 0),
    (["", ""], 0),
    (["", "", ""], 10),
    (["first line contains escape \\\\ here", " world"], 10),
    *[(choices(string_valid_examples_raw, k=2), spacing % 5) for spacing in range(10)],
]

string_invalid_examples: list[str] = [
    "'no end single quote",
    '"no end double quote',
    "'ambiguous single quotes'    '",
    '"ambiguous double quotes"    "\n',
    "'ambiguous single quotes'    \\'",
    "no start quote",
    "'no end single quote at newline    \\",
    "'no end single quote at newline    \\  '",
    "'chars after escape new line \\   ambiguous chars\n",
    "'nothing after escape new line \\    ",
    "'unknown escape sequence \\x'",
]


@pytest.mark.parametrize(
    "text_string", string_valid_examples_single + string_valid_examples_double
)
def test_valid_strings(text_string: str) -> None:
    """Test valid strings that do not escape to multiple lines."""
    text_string = simplify_escapes(text_string)
    result = tokenize_string(buffer=text_string, idx=0)
    assert result.token is not None
    assert result.token.tk_type == TokenType.JSON5_STRING
    assert result.token.value == text_string.strip().encode().decode("unicode_escape")


@pytest.mark.parametrize("text_strings, spacing", string_multi_lines_ext)
def test_valid_multiline_string(text_strings: list[str], spacing: int) -> None:
    """Test valid strings that escape to multiple lines."""
    original_string = "\n".join(text_strings).encode().decode("unicode_escape")
    original_string = f'"{original_string}"'
    multi_line_string = (
        f"\\{" " * spacing}{choice(list(LINE_TERMINATOR_SEQUENCE))}".join(text_strings)
    )
    multi_line_string = f'"{multi_line_string}"'
    multi_line_string = simplify_escapes(multi_line_string)
    result = tokenize_string(buffer=multi_line_string, idx=0)
    assert result.token is not None
    assert result.token.tk_type == TokenType.JSON5_STRING
    assert result.token.value == original_string


@pytest.mark.parametrize("text_string", string_invalid_examples)
def test_invalid_strings(text_string: str) -> None:
    """Test invalid strings."""
    with pytest.raises(JSON5DecodeError):
        tokenize_string(buffer=text_string, idx=0)
