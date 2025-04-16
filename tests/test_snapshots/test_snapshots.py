"""Snapshot tests for ujson5.
Snapshot tests are used to test the consistency of the dump and load functions.
If any of the tests fail, you should observe and confirm the changes before
re-generating the snapshots.
"""

import sys
from dataclasses import asdict

import pytest

import ujson5

from . import snapshots


def test_load_json5_from_composite_snapshots():
    """Test loading alpha snapshots."""
    for snapshot_name in snapshots.SNAPSHOT_NAMES.values():
        if (
            "composite_example" in snapshot_name
            and "special_separators" not in snapshot_name
        ):
            with open(
                snapshots.SNAPSHOTS_ROOT / snapshot_name, "r", encoding="utf8"
            ) as file:
                assert ujson5.load(file) == snapshots.COMPOSITE_EXAMPLE


def test_composite_default():
    """Test dump consistency."""
    with open(
        snapshots.SNAPSHOTS_ROOT
        / snapshots.SNAPSHOT_NAMES["composite_example_default"],
        "r",
        encoding="utf8",
    ) as file:
        assert ujson5.dumps(dict(snapshots.COMPOSITE_EXAMPLE)) == file.read().strip()


def test_composite_with_comments():
    """Test dump consistency."""
    if sys.version_info < (3, 12):
        # `__orig_bases__` is not available before Python 3.12,
        # we will find a way to test this in the future
        pytest.skip("Currently only support at least Python 3.12")
    with open(
        snapshots.SNAPSHOTS_ROOT
        / snapshots.SNAPSHOT_NAMES["composite_example_with_comments"],
        "r",
        encoding="utf8",
    ) as file:
        assert (
            ujson5.dumps(
                dict(snapshots.COMPOSITE_EXAMPLE),
                snapshots.Human,
                indent=snapshots.DEFAULT_INDENT,
            )
            == file.read().strip()
        )


def test_composite_no_comments():
    """Test dumping alpha without comments."""
    with open(
        snapshots.SNAPSHOTS_ROOT
        / snapshots.SNAPSHOT_NAMES["composite_example_no_comments"],
        "r",
        encoding="utf8",
    ) as file:
        assert (
            ujson5.dumps(
                dict(snapshots.COMPOSITE_EXAMPLE), indent=snapshots.DEFAULT_INDENT
            )
            == file.read().strip()
        )


def test_composite_no_indent():
    """Test dumping alpha without indent."""
    with open(
        snapshots.SNAPSHOTS_ROOT
        / snapshots.SNAPSHOT_NAMES["composite_example_no_indent"],
        "r",
        encoding="utf8",
    ) as file:
        assert ujson5.dumps(dict(snapshots.COMPOSITE_EXAMPLE)) == file.read().strip()


def test_composite_7_indent():
    """Test dumping alpha with 7 indent."""
    with open(
        snapshots.SNAPSHOTS_ROOT
        / snapshots.SNAPSHOT_NAMES["composite_example_7_indent"],
        "r",
        encoding="utf8",
    ) as file:
        assert (
            ujson5.dumps(dict(snapshots.COMPOSITE_EXAMPLE), indent=7)
            == file.read().strip()
        )


def test_composite_special_separators():
    """Test dumping alpha with special separators."""
    with open(
        snapshots.SNAPSHOTS_ROOT
        / snapshots.SNAPSHOT_NAMES["composite_example_special_separators"],
        "r",
        encoding="utf8",
    ) as file:
        assert (
            ujson5.dumps(
                dict(snapshots.COMPOSITE_EXAMPLE),
                indent=snapshots.DEFAULT_INDENT,
                separators=("|", "->"),
            )
            == file.read().strip()
        )


def test_composite_with_trailing_comma():
    """Test dumping alpha with trailing comma."""
    with open(
        snapshots.SNAPSHOTS_ROOT
        / snapshots.SNAPSHOT_NAMES["composite_example_with_trailing_comma"],
        "r",
        encoding="utf8",
    ) as file:
        assert (
            ujson5.dumps(
                dict(snapshots.COMPOSITE_EXAMPLE),
                indent=snapshots.DEFAULT_INDENT,
                trailing_comma=True,
            )
            == file.read().strip()
        )


def test_composite_no_trailing_comma():
    """Test dumping alpha without trailing comma."""
    with open(
        snapshots.SNAPSHOTS_ROOT
        / snapshots.SNAPSHOT_NAMES["composite_example_no_trailing_comma"],
        "r",
        encoding="utf8",
    ) as file:
        assert (
            ujson5.dumps(
                dict(snapshots.COMPOSITE_EXAMPLE),
                indent=snapshots.DEFAULT_INDENT,
                trailing_comma=False,
            )
            == file.read().strip()
        )


def test_pydantic_example():
    """Test dumping pydantic example."""
    with open(
        snapshots.SNAPSHOTS_ROOT / snapshots.SNAPSHOT_NAMES["pydantic_example"],
        "r",
        encoding="utf8",
    ) as file:
        assert (
            ujson5.dumps(
                snapshots.PYDANTIC_EXAMPLE.model_dump(),
                snapshots.CameraSlice,
                indent=snapshots.DEFAULT_INDENT,
            )
            == file.read().strip()
        )


def test_dataclass_example():
    """Test dumping data class example."""
    with open(
        snapshots.SNAPSHOTS_ROOT / snapshots.SNAPSHOT_NAMES["dataclass_example"],
        "r",
        encoding="utf8",
    ) as file:
        assert (
            ujson5.dumps(
                asdict(snapshots.DATA_CLASS_EXAMPLE),
                snapshots.Snapshot,
                indent=snapshots.DEFAULT_INDENT,
            )
            == file.read().strip()
        )
