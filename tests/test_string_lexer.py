"""Test the string lexer."""

from random import choice, choices, randint


import pytest

from ujson5.core import JSON5DecodeError, TOKEN_TYPE
from ujson5.lexer import (
    tokenize_string,
    simplify_escapes,
)
from ujson5.consts import (
    ESCAPE_SEQUENCE,
    LINE_TERMINATOR_SEQUENCE,
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
    "\ua3b2",
    "\u5232",
    *[f"hello\\{es}" for es in ESCAPE_SEQUENCE_NO_NL],
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


@pytest.mark.parametrize(
    "text_string", string_valid_examples_single + string_valid_examples_double
)
def test_valid_strings(text_string: str) -> None:
    """Test valid strings that do not escape to multiple lines."""
    text_string = simplify_escapes(text_string)
    result = tokenize_string(buffer=text_string, idx=0)
    assert result.token is not None
    assert result.token.tk_type == TOKEN_TYPE["STRING"]
    start, end = result.token.value
    assert text_string[start:end] == text_string.strip()[1:-1]
    assert text_string[result.idx - 1] in {'"', "'"}


@pytest.mark.parametrize("text_strings, spacing", string_multi_lines_ext)
def test_valid_multiline_string(text_strings: list[str], spacing: int) -> None:
    """Test valid strings that escape to multiple lines."""
    original_string = "\n".join(text_strings)
    original_string = f'"{original_string}"'
    multi_line_string = (
        f"\\{' ' * spacing}{choice(list(LINE_TERMINATOR_SEQUENCE))}".join(text_strings)
    )
    multi_line_string = f'"{multi_line_string}"'
    multi_line_string = simplify_escapes(multi_line_string)
    result = tokenize_string(buffer=multi_line_string, idx=0)
    assert result.token is not None
    assert result.token.tk_type == TOKEN_TYPE["STRING"]
    start, end = result.token.value
    assert multi_line_string[start:end] == multi_line_string[1:-1]
    assert multi_line_string[result.idx - 1] in {'"', "'"}


TEST_PASSAGE = """\"Lorem ipsum dolor sit wd, ws ads es.\\
Sed do hwe wer sd ut wd et rh magna hss. \\ua3b2 \\uabc2 \\
Ut tw ad minim we, ter qwe exercitation gs we nisi ut. \\
\\\' \\\" \\\\ \\b \\f \\n \\r \\t \\v \\0 \\xab \\u1234 \""""


def test_passage() -> None:
    """Test a passage."""
    result = tokenize_string(buffer=TEST_PASSAGE, idx=0)
    assert result.token is not None
    assert result.token.tk_type == TOKEN_TYPE["STRING"]
    start, end = result.token.value
    assert TEST_PASSAGE[start:end] == TEST_PASSAGE[1:-1]
    assert TEST_PASSAGE[result.idx - 1] in {'"', "'"}


string_invalid_examples: list[str] = [
    "'no end single quote",
    '"no end double quote',
    '"no end quote and new line\n',
    "no start quote",
    "'no end single quote at newline    \\",
    "'no end single quote at newline    \\  '",
    "'chars after escape new line \\   ambiguous chars\n",
    "'nothing after escape new line \\    ",
    "'unknown escape sequence \\x'",
    "'invalid unicode escape sequence \\u'",
    "'invalid unicode escape sequence \\u01'",
    "'invalid unicode escape sequence \\u013l'",
    "'invalid hex escape sequence \\x'",
    "'invalid hex escape sequence \\x1'",
    "'invalid hex escape sequence \\xz'",
    "'invalid escape sequence \\k'",
]


@pytest.mark.parametrize("text_string", string_invalid_examples)
def test_invalid_strings(text_string: str) -> None:
    """Test invalid strings."""
    with pytest.raises(JSON5DecodeError):
        tokenize_string(buffer=text_string, idx=0)
