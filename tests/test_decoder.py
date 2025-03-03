"""Tests for JSON5 parser."""

from math import isnan
from random import randint
from typing import Any
from collections.abc import Callable
from copy import copy

import pytest

import ujson5
from ujson5.consts import RESERVED_WORDS


BASIC_LOADS: list[tuple[str, Any]] = [
    ("null", None),
    ("true", True),
    ("false", False),
    ('"string"', "string"),
    ('"string with \\"escaped quotes\\""', 'string with "escaped quotes"'),
    ('"string with multiple \\\nlines"', "string with multiple lines"),
    ('"sig\u03a3ma"', "sigΣma"),
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
    ('{"sig\u03a3ma": "value"}', {"sigΣma": "value"}),
    ('{sig\u03a3ma: "value"}', {"sigΣma": "value"}),
]


@pytest.mark.parametrize(
    "json5, py_value",
    BASIC_LOADS,
)
def test_basic_loads(json5: str, py_value: Any) -> None:
    """Test basic JSON5 loads."""
    loaded: Any = ujson5.loads(json5)
    try:
        if not isnan(py_value):
            assert loaded == py_value
        else:
            assert isnan(loaded)
    except TypeError:
        assert loaded == py_value


@pytest.mark.parametrize(
    "json5, py_value",
    BASIC_LOADS,
)
def test_basic_loads_raw(json5: str, py_value: Any) -> None:
    """Test basic JSON5 loads."""
    str_len: int = len(json5)
    json5 += " " * randint(1, 10)
    loaded, idx = ujson5.Json5Decoder().raw_decode(json5)
    try:
        if not isnan(py_value):
            assert loaded == py_value
        else:
            assert isnan(loaded)
    except TypeError:
        assert loaded == py_value
    assert idx == str_len


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
def test_composite_loads(json5: str, py_value: ujson5.JsonValue) -> None:
    """Test composite JSON5 loads."""
    assert ujson5.loads(json5, strict=False) == py_value


@pytest.mark.parametrize("json5", ['"\\t"', '"\\n"', '"\\r"', '"\\0"'])
def test_strict_mode(json5: str) -> None:
    """Test composite JSON5 loads."""
    with pytest.raises(ujson5.JSON5DecodeError):
        ujson5.loads(json5, strict=True)


@pytest.mark.parametrize(
    "json5",
    [
        "null 1",
        "{key:}[12, }{: 12}12}",
        "12]",
        "{abc: abc}",
        ":34",
        ":{ab: 1232",
        "1}",
        "1:",
        "{1:",
        "abc\tdef",
        "{23",
        ":",
        "{",
        ",",
        ",11 11",
        "{abc: 12 def: 23}",
        "{'abc': 12 'def': 23}",
        "[12, 23:]",
        "{abc: 12, 23: 465}",
        "[12, 23, abc]",
        "[:",
        '{"abc":',
        '{"abc":3,23',
        "23,34",
        '{:"abc",]',
    ],
)
def test_invalid_loads(json5: str) -> None:
    """Test invalid JSON5 loads."""
    with pytest.raises(ujson5.JSON5DecodeError):
        ujson5.loads(json5)


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
    obj_hook: Callable[[dict[str, ujson5.JsonValue]], Any],
    py_value: ujson5.JsonValue,
) -> None:
    """Test composite JSON5 loads."""
    assert ujson5.loads(json5, object_hook=obj_hook) == py_value


@pytest.mark.parametrize(
    "json5, obj_pairs_hook, py_value",
    [
        (
            """{
    key6: 6,
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
    obj_pairs_hook: Callable[[ujson5.ObjectPairsHookArg], Any],
    py_value: ujson5.JsonValue,
) -> None:
    """Test composite JSON5 loads."""
    # object_pairs_hook takes priority over object_hook
    assert (
        ujson5.loads(json5, object_pairs_hook=obj_pairs_hook, object_hook=lambda v: 0)
        == py_value
    )


def test_invalid_object_hook() -> None:
    """Test invalid object hook."""
    with pytest.raises(ujson5.JSON5DecodeError):
        ujson5.loads("{}", object_hook=lambda v, k: 0)  # type: ignore

    with pytest.raises(ujson5.JSON5DecodeError):
        ujson5.loads("{}", object_pairs_hook=lambda v, k: 0)  # type: ignore


class CustomDecoder(ujson5.Json5Decoder):
    """Custom decoder class."""

    def __init__(self, *_: Any, **__: Any) -> None:
        super().__init__(parse_float=lambda v: float(v) + 1)


def test_custom_decoder() -> None:
    """Test custom decoder."""
    content = ujson5.loads(
        '{"key": 3.3}',
        cls=CustomDecoder,
    )
    assert content == {"key": 4.3}


NON_BOOL_RESERVED_WORDS = copy(RESERVED_WORDS)
NON_BOOL_RESERVED_WORDS.remove("true")
NON_BOOL_RESERVED_WORDS.remove("false")
NON_BOOL_RESERVED_WORDS.remove("null")


@pytest.mark.parametrize(
    "word",
    NON_BOOL_RESERVED_WORDS,
)
def test_reserved_word_keys(word: str) -> None:
    """Test reserved word keys."""
    with pytest.raises(ujson5.JSON5DecodeError):
        ujson5.loads(f"{{{word}: 1}}", allow_reserved_words=False)

    ujson5.loads(f"{{{word}: 1}}", allow_reserved_words=True)
