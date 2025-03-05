"""Test big list of naughty strings.
from https://github.com/minimaxir/big-list-of-naughty-strings"""

import os
from pathlib import Path

import ujson5

BLNS_PATH = Path(os.path.dirname(__file__)) / "blns" / "blns.json"


def test_blns() -> None:
    """Test for JSON checker files."""
    with open(BLNS_PATH, "r", encoding="utf-8") as file:
        ujson5.load(file, strict=False)
