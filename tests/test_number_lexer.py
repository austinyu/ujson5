from random import randint

import pytest

from pyjson5.core import JSON5DecodeError
from pyjson5.lexer import tokenize_number

valid_examples = [
    "0",
    "   0  ",
    "  3e2 ",
    "0e2",
    "123",
    "  123.456",
    ".123",
    "0.123",
    "99.99e10",
    "  99.99E+10",
    "1.2e-3",
    "0.0001  ",
    "123e5",
    ".5E10",
    "1.2E+0  ",
    "123.456e10  ",
    "   .001",
    "  123  ",
    "  0.456  ",
    "  7e10  ",
    "1e0",
    "1e+0",
    "1e-0",
    "1.23e10",
    "1.23e+10",
    "1.23e-10",
    "12345678901234567890",
    "1.2345678901234567890e+20",
]

valid_examples_entry = [f"{eg}," for eg in valid_examples]

valid_examples_entry_spaces = [f"{eg}{' ' * randint(1, 10)}," for eg in valid_examples]

valid_example_upper = [eg.upper() for eg in valid_examples]

invalid_examples = [
    "",
    "    ",
    "-",
    "+3",
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
    " 0d",
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
]


@pytest.mark.parametrize(
    "test_input",
    valid_examples
    + valid_examples_entry
    + valid_example_upper
    + valid_examples_entry_spaces,
)
def test_valid_literals(test_input):
    assert tokenize_number(buffer=test_input, idx=0).token is not None


@pytest.mark.parametrize("test_input", invalid_examples)
def test_invalid_literals(test_input):
    with pytest.raises(JSON5DecodeError):
        tokenize_number(buffer=test_input, idx=0)
