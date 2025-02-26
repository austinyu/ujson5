"""TODO"""

from collections.abc import Callable, Iterable
from typing import Any, TextIO, TypedDict, is_typeddict
import re
import inspect

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

COMMENTS_PATTERN = re.compile(
    r"(?P<block_comment>(?: *# *.+? *\n)*)"
    r" *(?P<name>\w+): *(?P<type>[^ ]+) *(?:# *(?P<inline_comment>.+))?\n"
)


class EntryComments(TypedDict):
    """Comments related to a TypedDict entry"""

    block_comments: list[str]
    inline_comment: str


CommentsCache = dict[str, EntryComments]


def extend_key_path(base_path: str, key: str) -> str:
    """Generate a unique name for each key in a composite dictionary by concatenating the
    base path and the key"""
    return f"{base_path}/{key}"


def get_comments(typed_dict_cls: Any) -> CommentsCache:
    """Extract comments from a TypedDict class"""
    assert is_typeddict(typed_dict_cls)

    comments: CommentsCache = {}

    def _get_comments(typed_dict_cls: Any, key_path: str) -> None:
        nonlocal comments

        # get comments from all inherit fields from parent TypedDict
        for base in typed_dict_cls.__orig_bases__:
            if is_typeddict(base):
                _get_comments(base, key_path)

        # get comments from current TypedDict
        source: str = inspect.getsource(typed_dict_cls)
        matches: Iterable[re.Match[str]] = COMMENTS_PATTERN.finditer(source)
        for match in matches:
            block_comment: str = match.group("block_comment").strip()
            name = match.group("name")
            inline_comment: str = match.group("inline_comment") or ""
            block_comments: list[str] = [
                comment.strip()[1:].strip()
                for comment in block_comment.split("\n")
                if comment.strip()
            ]
            comments[extend_key_path(key_path, name)] = {
                "block_comments": block_comments,
                "inline_comment": inline_comment,
            }
        # get comments from nested TypedDict
        for key, type_def in typed_dict_cls.__annotations__.items():
            if is_typeddict(type_def):
                _get_comments(type_def, extend_key_path(key_path, key))

    _get_comments(typed_dict_cls, key_path="")
    return comments


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
        quoted_keys: bool = False,
        trailing_comma: bool | None = None,
    ) -> None:
        self._skip_keys: bool = skip_keys
        self._ensure_ascii: bool = ensure_ascii
        self._allow_nan: bool = allow_nan
        self._sort_keys: bool = sort_keys
        self._indent_str: str | None = " " * indent if indent is not None else None
        self._item_separator: str = ", "
        self._key_separator: str = ": "
        self._quoted_keys: bool = quoted_keys
        if indent is not None:
            self._item_separator = ","
        self._trailing_comma: bool = indent is not None
        if trailing_comma is not None:
            self._trailing_comma = trailing_comma
        if separators is not None:
            self._item_separator, self._key_separator = separators

        if default is not None:
            setattr(self, "default", default)

        if check_circular:
            self._markers: dict[int, Any] | None = {}
        else:
            self._markers = None

        self._comments_cache: CommentsCache = {}

    def encode(self, obj: Any, typed_dict_cls: Any | None = None) -> str:
        """TODO"""
        if typed_dict_cls is not None and not is_typeddict(typed_dict_cls):
            raise JSON5EncodeError(EncoderErrors.invalid_typed_dict(typed_dict_cls))
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

        chunks = self.iterencode(obj, typed_dict_cls)
        if not isinstance(chunks, (list, tuple)):
            chunks = list(chunks)
        return "".join(chunks)

    def iterencode(self, obj: Any, typed_dict_cls: Any | None = None) -> Iterable[str]:
        """TODO"""
        if is_typeddict(typed_dict_cls):
            self._comments_cache = get_comments(typed_dict_cls)
        elif typed_dict_cls is not None:
            raise JSON5EncodeError(EncoderErrors.invalid_typed_dict(typed_dict_cls))
        return self._iterencode(obj, indent_level=0, key_path="")

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
        if key_str and not self._quoted_keys:
            return ESCAPE.sub(replace_unicode, obj)
        return f'"{ESCAPE.sub(replace_unicode, obj)}"'

    def _iterencode(self, obj: Any, indent_level: int, key_path: str) -> Iterable[str]:
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
            yield from self._iterencode_list(obj, indent_level, key_path)
        elif isinstance(obj, dict):
            yield from self._iterencode_dict(obj, indent_level, key_path)
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
            yield from self._iterencode(obj_user, indent_level, key_path)
            if self._markers is not None and marker_id is not None:
                del self._markers[marker_id]

    def _iterencode_list(
        self, obj: list | tuple, indent_level: int, key_path: str
    ) -> Iterable[str]:
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
                chunks = self._iterencode_list(value, indent_level, key_path)
            elif isinstance(value, dict):
                chunks = self._iterencode_dict(value, indent_level, key_path)
            else:
                chunks = self._iterencode(value, indent_level, key_path)
            yield from chunks
        comma = self._item_separator if self._trailing_comma else ""
        if self._indent_str is not None:
            indent_level -= 1
            yield comma + "\n" + self._indent_str * indent_level
        else:
            yield comma
        yield "]"
        if self._markers is not None and marker_id is not None:
            del self._markers[marker_id]

    def _iterencode_dict(
        self, obj: dict[Any, Any], indent_level: int, key_path: str
    ) -> Iterable[str]:
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
            yield newline_indent
        else:
            newline_indent = None
        first = True
        if self._sort_keys:
            items: Any = sorted(obj.items())
        else:
            items = obj.items()
        total_items: int = len(items)
        for idx, (key, value) in enumerate(items):
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
            specific_key_path: str = extend_key_path(key_path, key)
            block_comments: list[str] = self._comments_cache.get(  # type: ignore
                specific_key_path, {}
            ).get("block_comments", [])
            inline_comment: str = self._comments_cache.get(  # type: ignore
                specific_key_path, {}
            ).get("inline_comment", "")
            if first:
                first = False
            elif newline_indent is not None:
                yield newline_indent  # we do not need to yield anything if indent == 0
            for block_comment in block_comments:
                if newline_indent is not None:
                    yield f"// {block_comment}{newline_indent}"
            yield self._encode_str(key, key_str=True)
            yield self._key_separator
            if isinstance(value, (list, tuple)):
                chunks = self._iterencode_list(value, indent_level, specific_key_path)
            elif isinstance(value, dict):
                chunks = self._iterencode_dict(value, indent_level, specific_key_path)
            else:
                chunks = self._iterencode(value, indent_level, specific_key_path)
            yield from chunks

            if idx != total_items - 1:
                yield self._item_separator
            elif self._trailing_comma:
                yield self._item_separator
            if inline_comment and newline_indent is not None:
                yield "  // " + inline_comment
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
    quoted_keys=False,
    sort_keys=False,
    trailing_comma=None,
)


def dumps(
    obj: Any,
    typed_dict_cls: Any | None = None,
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
    quoted_keys: bool = False,
    trailing_comma: bool | None = None,
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
        and not quoted_keys
        and trailing_comma is None
    ):
        return _default_encoder.encode(obj, typed_dict_cls)
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
        quoted_keys=quoted_keys,
        trailing_comma=trailing_comma,
    ).encode(obj, typed_dict_cls)


def dump(
    obj: Any,
    fp: TextIO,
    typed_dict_cls: Any | None = None,
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
    quoted_keys: bool = False,
    trailing_comma: bool | None = None,
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
        and not quoted_keys
        and trailing_comma is None
    ):
        iterable = _default_encoder.iterencode(obj, typed_dict_cls)
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
            quoted_keys=quoted_keys,
            trailing_comma=trailing_comma,
        ).iterencode(obj, typed_dict_cls)
    for chunk in iterable:
        fp.write(chunk)
    fp.write("\n")
