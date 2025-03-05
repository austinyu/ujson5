"""JSON5 parser and serializer for Python."""

from .core import JsonValue, JSON5DecodeError, JSON5EncodeError
from .decoder import Json5Decoder, load, loads, ObjectPairsHookArg, ObjectHookArg
from .encoder import JSON5Encoder, dump, dumps, Serializable
from .__version__ import VERSION as version
from .__version__ import version_info

__all__ = [
    "version",
    "version_info",
    "JsonValue",
    "JSON5DecodeError",
    "JSON5EncodeError",
    "Json5Decoder",
    "load",
    "loads",
    "JSON5Encoder",
    "dumps",
    "dump",
    "ObjectPairsHookArg",
    "ObjectHookArg",
    "Serializable",
]
