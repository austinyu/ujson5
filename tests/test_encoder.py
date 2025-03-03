"""Test encoder."""

from typing import Any
from pathlib import Path

import pytest

import ujson5


@pytest.mark.parametrize(
    "py_obj, json5_obj",
    [
        ("string", '"string"'),
        (123, "123"),
        (123.456, "123.456"),
        (2e20, "2e+20"),
        (float("inf"), "Infinity"),
        (float("-inf"), "-Infinity"),
        (float("nan"), "NaN"),
        (True, "true"),
        (False, "false"),
        (None, "null"),
        ([], "[]"),
        ([1, 2, 3], "[1, 2, 3]"),
        ({}, "{}"),
        ({"key": "value"}, '{"key": "value"}'),
        ({"key": 123}, '{"key": 123}'),
        (
            {
                "string": "string",
                "int": 123,
                "float": 123.456,
                "true": True,
                "false": False,
                "null": None,
                "array": [1, 2, 3, [1, 2]],
                "heterogeneous": [1, 1.323, "string", True, None, {"key": "value"}],
                "object": {"key": "value"},
            },
            (
                '{"string": "string", "int": 123, "float": 123.456, "true": true, '
                '"false": false, "null": null, "array": [1, 2, 3, [1, 2]], '
                '"heterogeneous": [1, 1.323, "string", true, null, {"key": "value"}], '
                '"object": {"key": "value"}}'
            ),
        ),
        (
            {
                12: "int key",
                12.34: "float key",
                True: "bool key",
                False: "false key",
                None: "null key",
            },
            (
                '{"12": "int key", "12.34": "float key", "true": "bool key", '
                '"false": "false key", "null": "null key"}'
            ),
        ),
    ],
)
def test_valid_examples(py_obj: Any, json5_obj: str) -> None:
    """Test valid JSON5 examples."""
    assert ujson5.dumps(py_obj, check_circular=False) == json5_obj
    assert ujson5.dumps(py_obj, check_circular=True) == json5_obj


@pytest.mark.parametrize(
    "py_obj, json5_obj",
    [
        (
            {
                "val": 1,
                "array": [1, 2, 3],
                "obj": {"key": "value"},
            },
            """{
    "val": 1,
    "array": [
        1,
        2,
        3,
    ],
    "obj": {
        "key": "value",
    },
}""",
        )
    ],
)
def test_indent(py_obj: Any, json5_obj: str) -> None:
    """Test indent."""
    assert ujson5.dumps(py_obj, indent=4) == json5_obj


example_sets: Any = [
    set([1, 2, 3]),
    {"key": set([1, 2, 3])},
    [set([1, 2, 3])],
]


@pytest.mark.parametrize(
    "py_obj",
    example_sets,
)
def test_invalid_examples(py_obj: Any) -> None:
    """Test invalid JSON5 examples."""
    with pytest.raises(ujson5.JSON5EncodeError):
        ujson5.dumps(py_obj)


def test_skip_keys() -> None:
    """Test skip keys."""
    obj = {("non-string-key", "is here"): "value", "key2": "value2"}
    ujson5.dumps(obj, skip_keys=True)
    with pytest.raises(ujson5.JSON5EncodeError):
        ujson5.dumps(obj, skip_keys=False)


@pytest.mark.parametrize(
    "py_obj",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
    ],
)
def test_nan_not_allowed(py_obj: float) -> None:
    """Test NaN not allowed."""
    ujson5.dumps(py_obj, allow_nan=True)

    with pytest.raises(ujson5.JSON5EncodeError):
        ujson5.dumps(py_obj, allow_nan=False)


def test_circular_ref() -> None:
    """Test circular reference."""
    obj: dict = {}
    obj["self"] = obj
    with pytest.raises(ujson5.JSON5EncodeError):
        ujson5.dumps(obj)

    lst: list = []
    lst.append(obj)
    with pytest.raises(ujson5.JSON5EncodeError):
        ujson5.dumps(lst)

    lst = []
    lst.append(lst)
    with pytest.raises(ujson5.JSON5EncodeError):
        ujson5.dumps(lst)

    obj = {}
    obj["list"] = []
    obj["list"].append(obj)
    with pytest.raises(ujson5.JSON5EncodeError):
        ujson5.dumps(obj)

    class Custom:
        """Custom class."""

        def __init__(self, value: Any) -> None:
            self.value = value

    subset = Custom(1)
    subset.value = subset
    with pytest.raises(ujson5.JSON5EncodeError):
        ujson5.dumps(subset, default=lambda v: v.value)

    subset = Custom(1)
    ujson5.dumps(subset, default=lambda v: v.value, check_circular=False)


def test_sort_keys() -> None:
    """Test sort keys."""
    obj = {"key2": "value2", "key1": "value1"}
    assert ujson5.dumps(obj, sort_keys=True) == '{"key1": "value1", "key2": "value2"}'
    assert ujson5.dumps(obj, sort_keys=False) == '{"key2": "value2", "key1": "value1"}'


def test_default_set() -> None:
    """Test default set."""
    py_set = set([1, 2, 3])
    ujson5.dumps(py_set, default=list)

    py_lst = [1, 2, 3, set([1, 2, 3])]
    ujson5.dumps(py_lst, default=list)


def test_separators() -> None:
    """Test separators."""
    py_obj = {"key1": "value1", "key2": "value2"}
    assert (
        ujson5.dumps(py_obj, separators=(",", ":"))
        == '{"key1":"value1","key2":"value2"}'
    )
    assert (
        ujson5.dumps(py_obj, separators=(",", ": "))
        == '{"key1": "value1","key2": "value2"}'
    )
    assert (
        ujson5.dumps(py_obj, separators=("|", ">"))
        == '{"key1">"value1"|"key2">"value2"}'
    )


def test_replace_unicode() -> None:
    """Test unicode replacement"""
    py_obj = f"Hello\nWorld {chr(0x19)}"
    uni_char = f"\\u{0x19:04x}"
    expected_output = f'"Hello\\nWorld {uni_char}"'
    assert ujson5.dumps(py_obj, ensure_ascii=False) == expected_output


@pytest.mark.parametrize(
    "py_obj, json5_str",
    [
        ("Hello\x80World", '"Hello\\u0080World"'),
        # surrogate pair
        ("Hello\U0001f600World", '"Hello\\ud83d\\ude00World"'),
    ],
)
def test_replace_ascii(py_obj: str, json5_str: str) -> None:
    """Test ASCII replacement"""
    assert ujson5.dumps(py_obj, ensure_ascii=True) == json5_str


def test_invalid_typed_dict_cls(tmp_path: Path) -> None:
    """Test raise when TypedDict class is not valid."""
    with pytest.raises(ujson5.JSON5EncodeError):
        ujson5.dumps({}, typed_dict_cls=int)

    with pytest.raises(ujson5.JSON5EncodeError):
        with open(tmp_path / "dump.json5", "w", encoding="utf8") as file:
            ujson5.dump({}, file, typed_dict_cls=int)


def test_quoted_key() -> None:
    """Test quoted key."""
    obj = {"key": "value", "key2": "value2"}
    assert ujson5.dumps(obj, key_quotation="none") == '{key: "value", key2: "value2"}'
    assert (
        ujson5.dumps(obj, key_quotation="double")
        == '{"key": "value", "key2": "value2"}'
    )
    assert (
        ujson5.dumps(obj, key_quotation="single")
        == "{'key': \"value\", 'key2': \"value2\"}"
    )
