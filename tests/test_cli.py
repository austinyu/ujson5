"""Test cli functionally."""

import io
from contextlib import redirect_stdout
from pathlib import Path
from random import choice

import pytest
import ujson5
from ujson5 import cli

from . import example_consts


@pytest.mark.parametrize("arg", ["--version", "-v"])
def test_cli_version(arg: str) -> None:
    """Test version output."""
    with redirect_stdout(io.StringIO()) as f:
        cli.main([arg])
    assert f.getvalue().strip() == ujson5.version


@pytest.mark.parametrize("arg", ["--info", "-i"])
def test_cli_info(arg: str) -> None:
    """Test version info output."""
    with redirect_stdout(io.StringIO()) as f:
        cli.main([arg])
    assert f.getvalue().strip() == ujson5.version_info()


def test_cli_stdout_correct() -> None:
    """Test stdout output."""
    with redirect_stdout(io.StringIO()) as f:
        cli.main([str(choice(example_consts.VALID_EXAMPLES))])
    assert cli.JSON_CONVERTED in f.getvalue().strip()


def test_cli_stdout_incorrect() -> None:
    """Test stdout output."""
    with redirect_stdout(io.StringIO()) as f:
        cli.main([str(choice(example_consts.INVALID_EXAMPLES))])
    assert cli.DECODING_ERROR in f.getvalue().strip()


def test_cli_no_target(monkeypatch) -> None:
    """Test no target."""
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    with redirect_stdout(io.StringIO()) as f:
        cli.main([])
    assert cli.ERR_NO_TARGET in f.getvalue().strip()


def test_cli_stdin(monkeypatch) -> None:
    """Test reading from stdin with options."""
    monkeypatch.setattr("sys.stdin", io.StringIO('{"json": "obj"}'))
    with redirect_stdout(io.StringIO()) as f:
        cli.main(["--no-indent"])
    assert '{"json": "obj"}' in f.getvalue().strip()
    assert cli.JSON_CONVERTED in f.getvalue().strip()

    monkeypatch.setattr("sys.stdin", io.StringIO('{"json": "obj"}'))
    with redirect_stdout(io.StringIO()) as f:
        cli.main(["--compact"])
    assert '{"json":"obj"}' in f.getvalue().strip()
    assert cli.JSON_CONVERTED in f.getvalue().strip()


def test_cli_invalid_path() -> None:
    """Test invalid path."""
    with redirect_stdout(io.StringIO()) as f:
        cli.main([str(choice(example_consts.INVALID_EXAMPLES).parent / "wrong.json5")])
    assert cli.ERR_TARGET_NOT_EXIST in f.getvalue().strip()


def test_cli_output(tmp_path: Path) -> None:
    """Test output file."""
    target: Path = choice(example_consts.VALID_EXAMPLES)
    output: Path = tmp_path / "output.json5"
    assert not output.exists()
    cli.main([str(target), str(output)])
    assert output.exists()
