"""Tests for the number lexer."""

from random import randint

import pytest

from pyjson5.core import JSON5DecodeError
from pyjson5.lexer import TokenType, tokenize_number
from pyjson5.err_msg import NumberLexerErrors, LexerErrors

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


number_invalid_examples: list[tuple[str, str | None]] = [
    ("", NumberLexerErrors.no_number()),
    ("    ", NumberLexerErrors.unexpected_char_in_number(" ")),
    ("-", NumberLexerErrors.no_number()),
    ("00", NumberLexerErrors.leading_zero_followed_by_digit()),
    ("0123", NumberLexerErrors.leading_zero_followed_by_digit()),
    ("123 456", NumberLexerErrors.space_in_number()),
    ("1.2.3", NumberLexerErrors.unexpected_char_in_number(".")),
    ("1e", NumberLexerErrors.trailing_exponent()),
    ("1e+", NumberLexerErrors.trailing_exponent_sign()),
    (".e2", NumberLexerErrors.unexpected_char_in_number("e")),
    (". 123", NumberLexerErrors.unexpected_char_in_number(" ")),
    ("4.5e ", NumberLexerErrors.unexpected_char_in_number(" ")),
    ("4.5e+ ", NumberLexerErrors.unexpected_char_in_number(" ")),
    ("5.", NumberLexerErrors.trailing_dot()),
    ("5.5.5", NumberLexerErrors.unexpected_char_in_number(".")),
    ("1.", NumberLexerErrors.trailing_dot()),
    ("1 e3", NumberLexerErrors.space_in_number()),
    ("0d", NumberLexerErrors.unexpected_char_in_number("d")),
    (" 2f", NumberLexerErrors.unexpected_char_in_number(" ")),
    (" 2ei", NumberLexerErrors.unexpected_char_in_number(" ")),
    ("2e9d", NumberLexerErrors.unexpected_char_in_number("d")),
    ("123a", NumberLexerErrors.unexpected_char_in_number("a")),
    ("1.2.3", NumberLexerErrors.unexpected_char_in_number(".")),
    ("1e2e3", NumberLexerErrors.unexpected_char_in_number("e")),
    ("1..2", NumberLexerErrors.unexpected_char_in_number(".")),
    ("1.2.3", NumberLexerErrors.unexpected_char_in_number(".")),
    ("1e+e", NumberLexerErrors.unexpected_char_in_number("e")),
    ("1e-.", NumberLexerErrors.unexpected_char_in_number(".")),
    ("0123", NumberLexerErrors.leading_zero_followed_by_digit()),
    ("00.123", NumberLexerErrors.leading_zero_followed_by_digit()),
    ("1 2", NumberLexerErrors.space_in_number()),
    ("1. 2", NumberLexerErrors.unexpected_char_in_number(" ")),
    ("1e 2", NumberLexerErrors.unexpected_char_in_number(" ")),
    ("123abc", NumberLexerErrors.unexpected_char_in_number("a")),
    ("1.23e10xyz", NumberLexerErrors.unexpected_char_in_number("x")),
    (".", NumberLexerErrors.trailing_dot()),
    ("e", NumberLexerErrors.unexpected_char_in_number("e")),
    ("e10", NumberLexerErrors.unexpected_char_in_number("e")),
    ("1e+", NumberLexerErrors.trailing_exponent_sign()),
    ("1e-", NumberLexerErrors.trailing_exponent_sign()),
    ("+", NumberLexerErrors.no_number()),
    ("-", NumberLexerErrors.no_number()),
    ("e", NumberLexerErrors.unexpected_char_in_number("e")),
    ("E", NumberLexerErrors.unexpected_char_in_number("E")),
    ("0x", NumberLexerErrors.no_hex_digits()),
    ("0xG", NumberLexerErrors.unexpected_char_in_number("G")),
    ("0x1.23", NumberLexerErrors.unexpected_char_in_number(".")),
    ("0Xx", NumberLexerErrors.unexpected_char_in_number("x")),
    ("Inf", LexerErrors.unexpected_eof()),
    ("+Inf", LexerErrors.unexpected_eof()),
    ("Na", LexerErrors.unexpected_eof()),
    ("-Na", LexerErrors.unexpected_eof()),
    ("infinity", NumberLexerErrors.unexpected_char_in_number("i")),
    ("InfinityHere", NumberLexerErrors.unexpected_char_in_number("H")),
    ("NaNHere", NumberLexerErrors.unexpected_char_in_number("H")),
    ("+InfinityHere", NumberLexerErrors.unexpected_char_in_number("H")),
    ("-NaNHere", NumberLexerErrors.unexpected_char_in_number("H")),
    ("InfinitY", NumberLexerErrors.invalid_constant("Infinity", "InfinitY")),
    ("Nan", NumberLexerErrors.invalid_constant("NaN", "Nan")),
    ("+InfinitY", NumberLexerErrors.invalid_constant("Infinity", "InfinitY")),
    ("-Nan", NumberLexerErrors.invalid_constant("NaN", "Nan")),
    ("nan", NumberLexerErrors.unexpected_char_in_number("n")),
    ("+infinity", NumberLexerErrors.unexpected_char_in_number("i")),
    ("-infinity", NumberLexerErrors.unexpected_char_in_number("i")),
    ("+nan", NumberLexerErrors.unexpected_char_in_number("n")),
    ("-nan", NumberLexerErrors.unexpected_char_in_number("n")),
    ("Infinity Infinity", NumberLexerErrors.space_in_number()),
    ("InfinityInfinity", NumberLexerErrors.unexpected_char_in_number("I")),
    ("InfinityK", NumberLexerErrors.unexpected_char_in_number("K")),
    ("NaN NaN", NumberLexerErrors.space_in_number()),
    ("NaNNad", NumberLexerErrors.unexpected_char_in_number("N")),
    ("NaNN", NumberLexerErrors.unexpected_char_in_number("N")),
    ("0 0", NumberLexerErrors.space_in_number()),
    ("12 12,", NumberLexerErrors.space_in_number()),
    ("123.456 123.456", NumberLexerErrors.space_in_number()),
    ("1.2e-3 1.2e-3", NumberLexerErrors.space_in_number()),
    ("0x0 0x0", NumberLexerErrors.space_in_number()),
    ("0x1 0x1    ", NumberLexerErrors.space_in_number()),
    ("++", None),
    ("-  -", NumberLexerErrors.unexpected_char_in_number(" ")),
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


@pytest.mark.parametrize("text_number, err", number_invalid_examples)
def test_invalid_invalid_numbers(text_number: str, err: str) -> None:
    """Test invalid numbers."""
    with pytest.raises(JSON5DecodeError, match=err):
        tokenize_number(buffer=text_number, idx=0)
