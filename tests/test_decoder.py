"""Tests for JSON5 parser."""

from math import isnan
from typing import Any
from collections.abc import Callable
from os.path import join, dirname

import pytest

import pyjp5 as pj


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
    loaded: Any = pj.loads(json5)
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
def test_composite_loads(json5: str, py_value: pj.JsonValue) -> None:
    """Test composite JSON5 loads."""
    assert pj.loads(json5, strict=False) == py_value


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
        "1}",
        "1:",
        "{1:",
        "abc\\tdef",
    ],
)
def test_invalid_loads(json5: str) -> None:
    """Test invalid JSON5 loads."""
    with pytest.raises(pj.JSON5DecodeError):
        v = pj.loads(json5)
        print(v)


def test_config_file() -> None:
    """Test config file"""
    with open(join(dirname(__file__), "config.json5"), "r", encoding="utf8") as file:
        results = pj.load(file)
    assert results  # Add appropriate assertions based on expected tokens


@pytest.mark.parametrize(
    "json5, obj_hook, py_value",
    [
        (
            """{
    key1: 1,
    "key2": 2,
    "key3": 3,
    "key4": 4,
    "key5": 5,
    key6: 6
}""",
            lambda py_obj: {k.upper(): v + 1 for k, v in py_obj.items()},
            {
                "KEY1": 2,
                "KEY2": 3,
                "KEY3": 4,
                "KEY4": 5,
                "KEY5": 6,
                "KEY6": 7,
            },
        ),
        ("3", lambda v: v, 3),
    ],
)
def test_object_hook(
    json5: str,
    obj_hook: Callable[[dict[str, pj.JsonValue]], Any],
    py_value: pj.JsonValue,
) -> None:
    """Test composite JSON5 loads."""
    assert pj.loads(json5, object_hook=obj_hook) == py_value


@pytest.mark.parametrize(
    "json5, obj_pairs_hook, py_value",
    [
        (
            """{
    key6: 6
    "key3": 3,
    "key5": 5,
    key1: 1,
    "key2": 2,
    "key4": 4,
}""",
            lambda py_obj_pairs: [(k.upper(), v + 1) for k, v in py_obj_pairs],
            [
                ("KEY6", 7),
                ("KEY3", 4),
                ("KEY5", 6),
                ("KEY1", 2),
                ("KEY2", 3),
                ("KEY4", 5),
            ],
        ),
        ("3", lambda v: v, 3),
    ],
)
def test_object_pair_hook(
    json5: str,
    obj_pairs_hook: Callable[[tuple[str, pj.JsonValue]], Any],
    py_value: pj.JsonValue,
) -> None:
    """Test composite JSON5 loads."""
    assert pj.loads(json5, object_pairs_hook=obj_pairs_hook) == py_value
