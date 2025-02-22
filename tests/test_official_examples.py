"""Test cases provided by the official JSON5 test suite.

https://github.com/json5/json5-tests
"""

from os.path import dirname, join
from os import listdir
from pathlib import Path
import re


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

VALID_EXAMPLES = [
    join(EXAMPLE_ROOT, cat, f)
    for cat in CATEGORIES
    for f in listdir(join(EXAMPLE_ROOT, cat))
    if f.endswith(".json5") or f.endswith(".json")
]

INVALID_EXAMPLES = [
    join(EXAMPLE_ROOT, cat, f)
    for cat in CATEGORIES
    for f in listdir(join(EXAMPLE_ROOT, cat))
    if f.endswith(".js") or f.endswith(".txt")
]


@pytest.mark.parametrize(
    "path",
    VALID_EXAMPLES,
)
def test_valid_examples(path: str) -> None:
    """Test valid JSON5 examples."""
    with open(path, "r", encoding="utf8") as file:
        pyjp5.load(file)


@pytest.mark.parametrize(
    "path",
    INVALID_EXAMPLES,
)
def test_invalid_examples(path: str) -> None:
    """Test invalid JSON5 examples."""
    with open(path, "r", encoding="utf8") as file:
        with pytest.raises(pyjp5.JSON5DecodeError):
            pyjp5.load(file)


@pytest.mark.parametrize(
    "path",
    VALID_EXAMPLES,
)
def test_dump_load_examples(path: str, tmp_path: Path) -> None:
    """Test valid JSON5 examples."""
    with open(path, "r", encoding="utf8") as file:
        py_obj = pyjp5.load(file)
    dump_path_config = tmp_path / "dump_config.json5"
    dump_path_default = tmp_path / "dump_default.json5"
    with open(path, "r", encoding="utf8") as file:
        orig_content: str = file.read()
    non_ascii = bool(re.search(r"[^\x00-\x7F]", orig_content))
    with open(dump_path_config, "w", encoding="utf8") as file:
        pyjp5.dump(py_obj, file, indent=4, ensure_ascii=not non_ascii)

    with open(dump_path_default, "w", encoding="utf8") as file:
        pyjp5.dump(py_obj, file, indent=4, ensure_ascii=not non_ascii)

    with open(dump_path_config, "r", encoding="utf8") as file:
        new_content = pyjp5.load(file)

    with open(dump_path_default, "r", encoding="utf8") as file:
        new_content_default = pyjp5.load(file)

    if str(py_obj) == "nan":
        assert str(new_content) == "nan"
        assert str(new_content_default) == "nan"
        return
    assert py_obj == new_content == new_content_default
