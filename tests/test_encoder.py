"""Test encoder."""

from typing import Any

import pytest


import pyjp5


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
    assert pyjp5.dumps(py_obj, check_circular=False) == json5_obj
    assert pyjp5.dumps(py_obj, check_circular=True) == json5_obj


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
        3
    ],
    "obj": {
        "key": "value"
    }
}""",
        )
    ],
)
def test_indent(py_obj: Any, json5_obj: str) -> None:
    """Test indent."""
    assert pyjp5.dumps(py_obj, indent=4) == json5_obj


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
    with pytest.raises(pyjp5.JSON5EncodeError):
        pyjp5.dumps(py_obj)


def test_skip_keys() -> None:
    """Test skip keys."""
    obj = {("non-string-key", "is here"): "value", "key2": "value2"}
    pyjp5.dumps(obj, skip_keys=True)
    with pytest.raises(pyjp5.JSON5EncodeError):
        pyjp5.dumps(obj, skip_keys=False)


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
    pyjp5.dumps(py_obj, allow_nan=True)

    with pytest.raises(pyjp5.JSON5EncodeError):
        pyjp5.dumps(py_obj, allow_nan=False)


def test_circular_ref() -> None:
    """Test circular reference."""
    obj: dict = {}
    obj["self"] = obj
    with pytest.raises(pyjp5.JSON5EncodeError):
        pyjp5.dumps(obj)

    lst: list = []
    lst.append(obj)
    with pytest.raises(pyjp5.JSON5EncodeError):
        pyjp5.dumps(lst)

    obj = {}
    obj["list"] = []
    obj["list"].append(obj)
    with pytest.raises(pyjp5.JSON5EncodeError):
        pyjp5.dumps(obj)


def test_sort_keys() -> None:
    """Test sort keys."""
    obj = {"key2": "value2", "key1": "value1"}
    assert pyjp5.dumps(obj, sort_keys=True) == '{"key1": "value1", "key2": "value2"}'
    assert pyjp5.dumps(obj, sort_keys=False) == '{"key2": "value2", "key1": "value1"}'


def test_default_set() -> None:
    """Test default set."""
    py_obj = set([1, 2, 3])
    pyjp5.dumps(py_obj, default=list)

    pyjp5.dumps(py_obj, default=lambda _: '"string"')

    pyjp5.dumps(py_obj, default=lambda _: 1)

    pyjp5.dumps(py_obj, default=lambda _: 2.4)

    pyjp5.dumps(py_obj, default=lambda _: True)

    pyjp5.dumps(py_obj, default=lambda _: False)

    pyjp5.dumps(py_obj, default=lambda _: None)
