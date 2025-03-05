"""https://github.com/miloyip/nativejson-benchmark"""

import os
from pathlib import Path

import pytest
import ujson5

BASE_FOLDER = Path(os.path.dirname(__file__)) / "native_json_benchmark"

JSON_CHECKER_FOLDER = BASE_FOLDER / "jsonchecker"
JSON_CHECKER_PATHS: list[Path] = [
    f for f in JSON_CHECKER_FOLDER.iterdir() if f.is_file() if f.name.startswith("pass")
]


@pytest.mark.parametrize("file_path", JSON_CHECKER_PATHS)
def test_json_checker_file(file_path: Path) -> None:
    """Test for JSON checker files."""
    with open(file_path, "r", encoding="utf8") as file:
        ujson5.load(file, strict=False)


ROUND_TRIP_FOLDER = BASE_FOLDER / "roundtrip"
ROUND_TRIP_PATHS: list[Path] = list(ROUND_TRIP_FOLDER.iterdir())


@pytest.mark.parametrize("file_path", ROUND_TRIP_PATHS)
def test_round_trips(file_path: Path) -> None:
    """Test for loading and dumping."""
    with open(file_path, "r", encoding="utf8") as file:
        data = ujson5.load(file, strict=False)
        assert data == ujson5.loads(ujson5.dumps(data))


@pytest.mark.skipif(not os.getenv("CI_ENV"), reason="Run only in CI environment")
def test_loading_canada_file(benchmark) -> None:  # pragma: no cover
    """Test for loading large files."""
    with open(BASE_FOLDER / "canada.json", "r", encoding="utf8") as file:
        content: str = file.read()
    benchmark(ujson5.loads, content, strict=False)


@pytest.mark.skipif(not os.getenv("CI_ENV"), reason="Run only in CI environment")
def test_loading_citm_catalog_file(benchmark) -> None:  # pragma: no cover
    """Test for loading large files."""
    with open(BASE_FOLDER / "citm_catalog.json", "r", encoding="utf8") as file:
        content: str = file.read()
    benchmark(ujson5.loads, content, strict=False)


@pytest.mark.skipif(not os.getenv("CI_ENV"), reason="Run only in CI environment")
def test_loading_citm_twitter_file(benchmark) -> None:  # pragma: no cover
    """Test for loading large files."""
    with open(BASE_FOLDER / "twitter.json", "r", encoding="utf8") as file:
        content: str = file.read()
    benchmark(ujson5.loads, content, strict=False)
