"""Test for JSON test suite.
https://github.com/nst/JSONTestSuite
"""

import os
from pathlib import Path

import pytest
import ujson5

BASE_FOLDER = Path(os.path.dirname(__file__)) / "json_test_suite"
PARSING_FOLDER = BASE_FOLDER / "test_parsing"
TRANSFORM_FOLDER = BASE_FOLDER / "test_transform"

PARSING_FNAMES: list[Path] = [
    f
    for f in PARSING_FOLDER.iterdir()
    if f.is_file()
    if f.name
    not in {
        # https://262.ecma-international.org/5.1/#sec-7.3
        # line separators should not be allowed in a JSON string
        # not sure why the test suite has them
        "y_string_u+2029_par_sep.json",
        "y_string_u+2028_line_sep.json",
    }
]
ACCEPTED_PATHS: list[Path] = [f for f in PARSING_FNAMES if f.name.startswith("y_")]
REJECTED_PATHS: list[Path] = [f for f in PARSING_FNAMES if f.name.startswith("n_")]
AMBIGUOUS_PATHS: list[Path] = [f for f in PARSING_FNAMES if f.name.startswith("i_")]


@pytest.mark.parametrize("file_path", ACCEPTED_PATHS)
def test_accepted_json(file_path: Path) -> None:
    """Any accepted JSON is a valid JSON5."""
    with open(file_path, "r", encoding="utf8") as file:
        ujson5.load(file, strict=False)
