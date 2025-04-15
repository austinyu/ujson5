"""JSON5 parser and serializer for Python."""

from . import _version
from .core import JSON5DecodeError, JSON5EncodeError, JsonValue, version_info
from .decoder import Json5Decoder, ObjectHookArg, ObjectPairsHookArg, load, loads
from .encoder import JSON5Encoder, Serializable, dump, dumps

__version__ = _version.__version__


__all__ = [
    "__version__",
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
