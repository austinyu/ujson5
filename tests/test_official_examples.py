"""Test cases provided by the official JSON5 test suite.

https://github.com/json5/json5-tests
"""

from os.path import dirname, join
from os import listdir

import pytest

import pyjp5

EXAMPLE_ROOT = join(dirname(__file__), "json5_examples")

CATEGORIES = [
    "arrays",
    "comments",
    "misc",
    "new-lines",
    "numbers",
    "objects",
    "strings",
    "todo",
]


@pytest.mark.parametrize(
    "path",
    [
        join(EXAMPLE_ROOT, cat, f)
        for cat in CATEGORIES
        for f in listdir(join(EXAMPLE_ROOT, cat))
        if f.endswith(".json5") or f.endswith(".json")
    ],
)
def test_valid_examples(path: str) -> None:
    """Test valid JSON5 examples."""
    with open(path, "r", encoding="utf8") as file:
        pyjp5.load(file)


@pytest.mark.parametrize(
    "path",
    [
        join(EXAMPLE_ROOT, cat, f)
        for cat in CATEGORIES
        for f in listdir(join(EXAMPLE_ROOT, cat))
        if f.endswith(".js") or f.endswith(".txt")
    ],
)
def test_invalid_examples(path: str) -> None:
    """Test invalid JSON5 examples."""
    with open(path, "r", encoding="utf8") as file:
        with pytest.raises(pyjp5.JSON5DecodeError):
            pyjp5.load(file)
