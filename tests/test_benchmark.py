"""Benchmark tests for pyjp5."""

import os

import pytest

import pyjp5

from . import example_consts


@pytest.mark.parametrize(
    "path",
    example_consts.VALID_EXAMPLES,
)
@pytest.mark.skipif(not os.getenv("CI_ENV"), reason="Run only in CI environment")
def test_pyjp5_benchmark(path: str, benchmark) -> None:
    """Test valid JSON5 examples."""
    with open(
        os.path.join(example_consts.EXAMPLE_ROOT, "arrays", path), "r", encoding="utf8"
    ) as file:
        content = file.read()
    benchmark(pyjp5.loads, content)
