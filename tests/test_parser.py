"""Tests for JSON5 parser."""

from math import isnan
from typing import Any
from os.path import join, dirname

import pytest

from pyjp5 import loads, JsonValue
from pyjp5.core import JSON5DecodeError

# JSON5Value:
# JSON5Null
# JSON5Boolean
# JSON5String
# JSON5Number
# JSON5Object
# JSON5Array


@pytest.mark.parametrize(
    "json5, py_value",
    [
        ("null", None),
        ("true", True),
        ("false", False),
        ('"string"', "string"),
        ('"string with \\"escaped quotes\\""', 'string with "escaped quotes"'),
        ('"string with multiple \\\nlines"', "string with multiple lines"),
        ("123", 123),
        ("123.456", 123.456),
        ("0x23", 0x23),
        ("23e-2", 23e-2),
        ("Infinity", float("inf")),
        ("NaN", float("nan")),
        ("-Infinity", float("-inf")),
        ("-NaN", float("-nan")),
        ("[1, 2, 3]", [1, 2, 3]),
        ('{"key": "value"}', {"key": "value"}),
    ],
)
def test_basic_loads(json5: str, py_value: Any) -> None:
    """Test basic JSON5 loads."""
    loaded: Any = loads(json5)
    try:
        if not isnan(py_value):
            assert loaded == py_value
        else:
            assert isnan(loaded)
    except TypeError:
        assert loaded == py_value


@pytest.mark.parametrize(
    "json5, py_value",
    [
        (
            """{
            key: "value",
            "key2": 123,
            "key3": true,
            "key4": null,
            "key5": [1, 2, 3],
            key6: {
                "nested": "object"
            }

         }
""",
            {
                "key": "value",
                "key2": 123,
                "key3": True,
                "key4": None,
                "key5": [1, 2, 3],
                "key6": {"nested": "object"},
            },
        ),
        (
            """
{
  // comments
  unquoted: 'and you can quote me on that',
  singleQuotes: 'I can use "double quotes" here',
  lineBreaks: "Look, Mom! \\
No \\n's!",
  hexadecimal: 0xdecaf,
  leadingDecimalPoint: .8675309, andTrailing: 8675309.,
  positiveSign: +1,
  trailingComma: 'in objects', andIn: ['arrays',],
  "backwardsCompatible": "with JSON",
  null_supported: null,
  infinities_supported: Infinity,
}
""",
            {
                "unquoted": "and you can quote me on that",
                "singleQuotes": 'I can use "double quotes" here',
                "lineBreaks": "Look, Mom! No \n's!",
                "hexadecimal": 0xDECAF,
                "leadingDecimalPoint": 0.8675309,
                "andTrailing": 8675309.0,
                "positiveSign": 1,
                "trailingComma": "in objects",
                "andIn": ["arrays"],
                "backwardsCompatible": "with JSON",
                "null_supported": None,
                "infinities_supported": float("inf"),
            },
        ),
    ],
)
def test_composite_loads(json5: str, py_value: JsonValue) -> None:
    """Test composite JSON5 loads."""
    assert loads(json5) == py_value


@pytest.mark.parametrize(
    "json5",
    [
        "null 1",
        "{key:}[12, }{: 12}12}",
        "12]",
        "{abc: abc}",
        ":34",
        ":{ab: 1232",
        '"abc \\ des"',
    ],
)
def test_invalid_loads(json5: str) -> None:
    """Test invalid JSON5 loads."""
    with pytest.raises(JSON5DecodeError):
        v = loads(json5)
        print(v)


def test_config_file() -> None:
    """Test config file"""
    with open(join(dirname(__file__), "config.json5"), "r", encoding="utf8") as file:
        config_content = file.read()
    results = loads(config_content)
    assert results  # Add appropriate assertions based on expected tokens
