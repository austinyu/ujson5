"""Tests for the number lexer."""

from random import randint

import pytest

from pyjson5.core import JSON5DecodeError
from pyjson5.lexer import TokenType, tokenize_number

number_valid_examples = [
    "0",
    "0",
    "3e2",
    "0e2",
    "123",
    "123.456",
    ".123",
    "0.123",
    "99.99e10",
    "99.99E+10",
    "1.2e-3",
    "0.0001",
    "123e5",
    ".5E10",
    "1.2E+0  ",
    "123.456e10  ",
    ".001",
    "123",
    "0.456",
    "7e10",
    "1e0",
    "1e+0",
    "1e-0",
    "1.23e10",
    "1.23e+10",
    "1.23e-10",
    "12345678901234567890",
    "1.2345678901234567890e+20",
    "0x0",
    "0x1",
    "0x123ABC",
    "0XABCDEF",
    "-123",
    "-123.456",
    "+0",
    "-0",
    "+.123",
    "-.434",
]

number_valid_constants = [
    "Infinity",
    "+Infinity",
    "-Infinity",
    "NaN",
    "+NaN",
    "-NaN",
]

number_valid_example_upper = [eg.upper() for eg in number_valid_examples]

number_valid_examples_spaces = [
    f"{eg}{' ' * randint(1, 10)}"
    for eg in number_valid_examples + number_valid_example_upper
]

number_valid_examples_spaces_entry = [
    f"{eg},{' ' * randint(1, 10)}"
    for eg in number_valid_examples_spaces + number_valid_example_upper
]


number_invalid_examples = [
    "",
    "    ",
    "-",
    "00",
    "0123",
    "123 456",
    "1.2.3",
    "1e",
    "1e+",
    ".e2",
    ". 123",
    "4.5e ",
    "4.5e+ ",
    "5.",
    "5.5.5",
    "1.",
    "1 e3",
    "0d",
    " 2f",
    " 2ei",
    "2e9d",
    "123a",
    "1.2.3",
    "1e2e3",
    "1..2",
    "1.2.3",
    "1e+e",
    "1e-.",
    "0123",
    "00.123",
    "1 2",
    "1. 2",
    "1e 2",
    "123abc",
    "1.23e10xyz",
    ".",
    "e",
    "e10",
    "1e+",
    "1e-",
    "+",
    "-",
    "e",
    "E",
    "0x",
    "0xG",
    "0x1.23",
    "0Xx",
    "Inf",
    "+Inf",
    "Na",
    "-Na",
    "infinity",
    "InfinityHere",
    "NaNHere",
    "+InfinityHere",
    "-NaNHere",
    "InfinitY",
    "Nan",
    "+InfinitY",
    "-Nan",
    "nan",
    "+infinity",
    "-infinity",
    "+nan",
    "-nan",
    "Infinity Infinity",
    "InfinityInfinity",
    "InfinityK",
    "NaN NaN",
    "NaNNad",
    "NaNN",
    "0 0",
    "12 12,",
    "123.456 123.456",
    "1.2e-3 1.2e-3",
    "0x0 0x0",
    "0x1 0x1    ",
    "++",
    "-  -",
]


@pytest.mark.parametrize(
    "text_number",
    number_valid_examples
    + number_valid_constants
    + number_valid_example_upper
    + number_valid_examples_spaces
    + number_valid_examples_spaces_entry,
)
def test_valid_numbers(text_number: str) -> None:
    """Test valid numbers."""
    result = tokenize_number(buffer=text_number, idx=0)
    assert result.token is not None
    assert result.token.tk_type == TokenType.JSON5_NUMBER
    if "," in text_number:
        assert result.token.value == text_number.strip()[:-1].strip()
    else:
        assert result.token.value == text_number.strip()


@pytest.mark.parametrize("text_number", number_invalid_examples)
def test_invalid_invalid_numbers(text_number: str) -> None:
    """Test invalid numbers."""
    with pytest.raises(JSON5DecodeError):
        tokenize_number(buffer=text_number, idx=0)
