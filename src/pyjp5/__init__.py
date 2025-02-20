"""JSON5 parser and serializer for Python."""

from .decoder import Json5Decoder, load, loads
from .core import JsonValue, JSON5DecodeError

__all__ = [
    "Json5Decoder",
    "load",
    "loads",
    "dumps",
    "dump",
    "JSON5DecodeError",
    "JsonValue",
]


def dumps(data: JsonValue) -> str:
    """Convert python data to JSON5 string."""
    raise NotImplementedError


def dump(data: JsonValue, file) -> None:
    """Convert python data to JSON5 string and write to file."""
    raise NotImplementedError
