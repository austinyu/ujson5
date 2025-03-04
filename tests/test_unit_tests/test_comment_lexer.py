"""Tests for comment lexer."""

import pytest

from ujson5.lexer import validate_comment


@pytest.mark.parametrize(
    "comment,end",
    [
        ("//", 2),
        ("// some comment is here\n new line", 24),
        ("/* some comment is here */", 26),
        ("/* some comment is here\n new line */", 36),
        ("/* some comment is here\n new line */ new line", 36),
    ],
)
def test_valid_comments(comment: str, end: int) -> None:
    """Test valid comments."""
    idx = validate_comment(comment, 0)
    assert idx == end


@pytest.mark.parametrize(
    "comment",
    [
        "/",
        "/*",
        "/* some comment is here",
        "/* some comment is here*",
    ],
)
def test_invalid_comments(comment: str) -> None:
    """Test invalid comments."""
    with pytest.raises(ValueError):
        validate_comment(comment, 0)
