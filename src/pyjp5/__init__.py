"""JSON5 parser and serializer for Python."""

from .lexer import tokenize
from .parser import parser
from .core import JsonValue


def dumps(data: JsonValue) -> str:
    """Convert python data to JSON5 string."""
    raise NotImplementedError


def dump(data: JsonValue, file) -> None:
    """Convert python data to JSON5 string and write to file."""
    raise NotImplementedError


def loads(data: str) -> JsonValue:
    """Convert JSON5 string to python data."""
    return parser(data, tokenize(data))


def load(file) -> JsonValue:
    """Convert JSON5 file to python data."""
    return loads(file.read())
