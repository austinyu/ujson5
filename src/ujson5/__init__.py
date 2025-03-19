"""JSON5 parser and serializer for Python."""

from .__version__ import VERSION as version
from .__version__ import version_info
from .core import JSON5DecodeError, JSON5EncodeError, JsonValue
from .decoder import Json5Decoder, ObjectHookArg, ObjectPairsHookArg, load, loads
from .encoder import JSON5Encoder, Serializable, dump, dumps

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
