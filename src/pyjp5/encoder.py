"""TODO"""

from collections.abc import Callable, Iterable
from typing import Any, TextIO
import re

from .core import JSON5EncodeError
from .err_msg import EncoderErrors

Serializable = dict | list | tuple | int | float | str | None | bool
DefaultInterface = (
    Callable[[Any], dict]
    | Callable[[Any], list]
    | Callable[[Any], tuple]
    | Callable[[Any], int]
    | Callable[[Any], float]
    | Callable[[Any], str]
    | Callable[[Any], None]
    | Callable[[Any], bool]
)

ESCAPE = re.compile(r'[\x00-\x1f\\"\b\f\n\r\t]')
ESCAPE_ASCII = re.compile(r'([\\"]|[^\ -~])')
HAS_UTF8 = re.compile(b"[\x80-\xff]")
ESCAPE_DCT = {
    "\\": "\\\\",
    '"': '\\"',
    "\b": "\\b",
    "\f": "\\f",
    "\n": "\\n",
    "\r": "\\r",
    "\t": "\\t",
}
for i in range(0x20):
    ESCAPE_DCT.setdefault(chr(i), f"\\u{i:04x}")


class JSON5Encoder:
    """TODO"""

    def __init__(
        self,
        *,
        default: DefaultInterface | None = None,
        skip_keys: bool = False,
        ensure_ascii: bool = True,
        check_circular: bool = True,
        allow_nan: bool = True,
        indent: int | None = None,
        separators: tuple[str, str] | None = None,
        sort_keys: bool = False,
        ensure_quoted_keys: bool = False,
    ) -> None:
        self._skip_keys: bool = skip_keys
        self._ensure_ascii: bool = ensure_ascii
        self._allow_nan: bool = allow_nan
        self._sort_keys: bool = sort_keys
        self._indent_str: str | None = " " * indent if indent is not None else None
        self._item_separator: str = ", "
        self._key_separator: str = ": "
        self._ensure_quoted_keys: bool = ensure_quoted_keys
        if indent is not None:
            self._item_separator = ","
        if separators is not None:
            self._item_separator, self._key_separator = separators

        if default is not None:
            setattr(self, "default", default)

        if check_circular:
            self._markers: dict[int, Any] | None = {}
        else:
            self._markers = None

    def encode(self, obj: Any) -> str:
        """TODO"""
        if isinstance(obj, str):
            return self._encode_str(obj)
        if isinstance(obj, bool):
            return "true" if obj else "false"
        if isinstance(obj, int):
            return self._encode_int(obj)
        if isinstance(obj, float):
            return self._encode_float(obj)
        if obj is None:
            return "null"

        chunks = self.iterencode(obj)
        if not isinstance(chunks, (list, tuple)):
            chunks = list(chunks)
        return "".join(chunks)

    def iterencode(self, obj: Any) -> Iterable[str]:
        """TODO"""
        return self._iterencode(obj, indent_level=0)

    def default(self, obj: Any) -> Serializable:
        """TODO"""
        raise JSON5EncodeError(EncoderErrors.unable_to_encode(obj))

    def _encode_int(self, obj: int) -> str:
        # Subclasses of int/float may override __repr__, but we still
        # want to encode them as integers/floats in JSON. One example
        # within the standard library is IntEnum.
        return int.__repr__(obj)

    def _encode_float(self, obj: float) -> str:
        if obj != obj:  # pylint: disable=R0124
            text = "NaN"
        elif obj == float("inf"):
            text = "Infinity"
        elif obj == float("-inf"):
            text = "-Infinity"
        else:
            return float.__repr__(obj)

        if not self._allow_nan:
            raise JSON5EncodeError(EncoderErrors.float_out_of_range(obj))

        return text

    def _encode_str(self, obj: str, key_str: bool = False) -> str:
        def replace_unicode(match: re.Match) -> str:
            return ESCAPE_DCT[match.group(0)]

        def replace_ascii(match: re.Match) -> str:
            s = match.group(0)
            try:
                return ESCAPE_DCT[s]
            except KeyError:
                n = ord(s)
                if n < 0x10000:
                    return f"\\u{n:04x}"
                # surrogate pair
                n -= 0x10000
                s1 = 0xD800 | ((n >> 10) & 0x3FF)
                s2 = 0xDC00 | (n & 0x3FF)
                return f"\\u{s1:04x}\\u{s2:04x}"

        if self._ensure_ascii:
            return f'"{ESCAPE_ASCII.sub(replace_ascii, obj)}"'
        if key_str and not self._ensure_quoted_keys:
            return ESCAPE.sub(replace_unicode, obj)
        return f'"{ESCAPE.sub(replace_unicode, obj)}"'

    def _iterencode(self, obj: Any, indent_level: int) -> Iterable[str]:
        if isinstance(obj, str):
            yield self._encode_str(obj)
        elif obj is None:
            yield "null"
        elif obj is True:
            yield "true"
        elif obj is False:
            yield "false"
        elif isinstance(obj, int):
            # see comment for int/float in _make_iterencode
            yield self._encode_int(obj)
        elif isinstance(obj, float):
            # see comment for int/float in _make_iterencode
            yield self._encode_float(obj)
        elif isinstance(obj, (list, tuple)):
            yield from self._iterencode_list(obj, indent_level)
        elif isinstance(obj, dict):
            yield from self._iterencode_dict(obj, indent_level)
        else:
            if self._markers is not None:
                marker_id: int | None = id(obj)
                if marker_id in self._markers:
                    raise JSON5EncodeError(EncoderErrors.circular_reference())
                assert marker_id is not None
                self._markers[marker_id] = obj
            else:
                marker_id = None
            obj_user = self.default(obj)
            yield from self._iterencode(obj_user, indent_level)
            if self._markers is not None and marker_id is not None:
                del self._markers[marker_id]

    def _iterencode_list(self, obj: list | tuple, indent_level: int) -> Iterable[str]:
        if not obj:
            yield "[]"
            return
        if self._markers is not None:
            marker_id: int | None = id(obj)
            if marker_id in self._markers:
                raise JSON5EncodeError(EncoderErrors.circular_reference())
            assert marker_id is not None
            self._markers[marker_id] = obj
        else:
            marker_id = None
        buffer = "["
        if self._indent_str is not None:
            indent_level += 1
            newline_indent: str | None = "\n" + self._indent_str * indent_level
            assert newline_indent is not None
            separator = self._item_separator + newline_indent
            buffer += newline_indent
        else:
            newline_indent = None
            separator = self._item_separator
        first: bool = True
        for value in obj:
            if first:
                first = False
            else:
                buffer = separator
            yield buffer
            if isinstance(value, (list, tuple)):
                chunks = self._iterencode_list(value, indent_level)
            elif isinstance(value, dict):
                chunks = self._iterencode_dict(value, indent_level)
            else:
                chunks = self._iterencode(value, indent_level)
            yield from chunks
        if self._indent_str is not None:
            indent_level -= 1
            yield "\n" + self._indent_str * indent_level
        yield "]"
        if self._markers is not None and marker_id is not None:
            del self._markers[marker_id]

    def _iterencode_dict(self, obj: dict[Any, Any], indent_level: int) -> Iterable[str]:
        if not obj:
            yield "{}"
            return
        if self._markers is not None:
            marker_id: int | None = id(obj)
            if marker_id in self._markers:
                raise JSON5EncodeError(EncoderErrors.circular_reference())
            assert marker_id is not None
            self._markers[marker_id] = obj
        else:
            marker_id = None
        yield "{"
        if self._indent_str is not None:
            indent_level += 1
            newline_indent: str | None = "\n" + self._indent_str * indent_level
            assert newline_indent is not None
            item_separator: str = self._item_separator + newline_indent
            yield newline_indent
        else:
            newline_indent = None
            item_separator = self._item_separator
        first = True
        if self._sort_keys:
            items: Any = sorted(obj.items())
        else:
            items = obj.items()
        for key, value in items:
            if isinstance(key, str):
                pass
            # JavaScript is weakly typed for these, so it makes sense to
            # also allow them.  Many encoders seem to do something like this.
            elif isinstance(key, (float, int, bool)) or key is None:
                key = "".join(list(self.iterencode(key)))
            elif self._skip_keys:
                continue
            else:
                raise JSON5EncodeError(EncoderErrors.invalid_key_type(key))
            if first:
                first = False
            else:
                yield item_separator
            yield self._encode_str(key, key_str=True)
            yield self._key_separator
            if isinstance(value, (list, tuple)):
                chunks = self._iterencode_list(value, indent_level)
            elif isinstance(value, dict):
                chunks = self._iterencode_dict(value, indent_level)
            else:
                chunks = self._iterencode(value, indent_level)
            yield from chunks
        if self._indent_str is not None:
            indent_level -= 1
            yield "\n" + self._indent_str * indent_level
        yield "}"
        if self._markers is not None and marker_id is not None:
            del self._markers[marker_id]


_default_encoder = JSON5Encoder(
    skip_keys=False,
    ensure_ascii=True,
    check_circular=True,
    allow_nan=True,
    indent=None,
    separators=None,
    default=None,
    ensure_quoted_keys=False,
    sort_keys=False,
)


def dumps(
    obj: Any,
    *,
    skip_keys: bool = False,
    ensure_ascii: bool = True,
    check_circular: bool = True,
    allow_nan: bool = True,
    cls: type[JSON5Encoder] | None = None,
    indent: int | None = None,
    separators: tuple[str, str] | None = None,
    default: DefaultInterface | None = None,
    sort_keys: bool = False,
    ensure_quoted_keys: bool = False,
) -> str:
    """TODO"""
    if (
        not skip_keys  # pylint: disable=R0916
        and ensure_ascii
        and check_circular
        and allow_nan
        and cls is None
        and indent is None
        and separators is None
        and default is None
        and not sort_keys
        and not ensure_quoted_keys
    ):
        return _default_encoder.encode(obj)
    if cls is None:
        cls = JSON5Encoder
    return cls(
        skip_keys=skip_keys,
        ensure_ascii=ensure_ascii,
        check_circular=check_circular,
        allow_nan=allow_nan,
        indent=indent,
        separators=separators,
        default=default,
        sort_keys=sort_keys,
        ensure_quoted_keys=ensure_quoted_keys,
    ).encode(obj)


def dump(
    obj: Any,
    fp: TextIO,
    *,
    skip_keys: bool = False,
    ensure_ascii: bool = True,
    check_circular: bool = True,
    allow_nan: bool = True,
    cls: type[JSON5Encoder] | None = None,
    indent: int | None = None,
    separators: tuple[str, str] | None = None,
    default: DefaultInterface | None = None,
    sort_keys: bool = False,
    ensure_quoted_keys: bool = False,
) -> None:
    """TODO"""
    if (
        not skip_keys  # pylint: disable=R0916
        and ensure_ascii
        and check_circular
        and allow_nan
        and cls is None
        and indent is None
        and separators is None
        and default is None
        and not sort_keys
        and not ensure_quoted_keys
    ):
        iterable = _default_encoder.iterencode(obj)
    else:
        if cls is None:
            cls = JSON5Encoder
        iterable = cls(
            skip_keys=skip_keys,
            ensure_ascii=ensure_ascii,
            check_circular=check_circular,
            allow_nan=allow_nan,
            indent=indent,
            separators=separators,
            default=default,
            sort_keys=sort_keys,
            ensure_quoted_keys=ensure_quoted_keys,
        ).iterencode(obj)
    for chunk in iterable:
        fp.write(chunk)
