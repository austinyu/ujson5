"""Implements the JSON5Encoder class and the dumps and dump functions."""

import inspect
import re
import sys
import tokenize
from collections.abc import Callable, Iterable
from io import StringIO
from typing import Any, Literal, TextIO, TypedDict, is_typeddict
from warnings import warn

from ujson5.core import JSON5EncodeError
from ujson5.err_msg import EncoderErrors

Serializable = dict | list | tuple | int | float | str | None | bool
"""Python objects that can be serialized to JSON5"""

DefaultInterface = (
    Callable[[Any], dict]
    | Callable[[Any], list]
    | Callable[[Any], tuple]
    | Callable[[Any], int]
    | Callable[[Any], float]
    | Callable[[Any], str]
    | Callable[[Any], None]
    | Callable[[Any], bool]
    | Callable[[Any], Serializable]
)
"""A callable that takes in an object that is not
serializable and returns a serializable object"""

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
    + r" *(?P<name>\w+): *(?P<type>[^#^\n]+) *(?:# *(?P<inline_comment>.+))?\n"
)


class EntryComments(TypedDict):
    """Comments related to a TypedDict entry"""

    block_comments: list[str]
    inline_comment: str


CommentsCache = dict[str, EntryComments]


def extend_key_path(base_path: str, key: str) -> str:
    """Generate a unique name for each key in a composite dictionary by concatenating the
    base path and the key

    Args:
        base_path: The base path
        key: The key to be added to the base path

    Returns:
        str: The extended key path
    """
    return f"{base_path}/{key}"


def get_comments(data_model: Any) -> CommentsCache:
    """Extract comments from a data model class

    Warning:
        Comments extraction is currently only fully supported on Python 3.12+. On older
        versions, the function will still work but will not extract all comments from the
        parent data models.

    Args:
        data_model: Class based data model (e.g. TypedDict, dataclass, etc.)

    Returns:
        CommentsCache: A dictionary containing comments related to each data model entry
    """

    def _get_comments(
        data_model: Any, key_path: str, comments: CommentsCache
    ) -> CommentsCache:
        def update_comments():
            nonlocal comments, block_comments, inline_comment, field_name
            comments[extend_key_path(key_path, field_name)] = {
                "block_comments": block_comments,
                "inline_comment": inline_comment,
            }
            block_comments = []
            inline_comment = ""
            field_name = ""

        def is_prev_not_block_comment(idx: int) -> bool:
            # for first indented line in a block, INDENT is a token, but for all the following
            # lines, indent is not tokenized.
            if idx > 1 and tokens[idx - 1].type == tokenize.INDENT:
                # first indented line in a block
                return (
                    idx > 3
                    and tokens[idx - 3].type != tokenize.COMMENT
                    or tokens[idx - 4].string != "\n"
                )
            return (
                idx > 2
                and tokens[idx - 2].type != tokenize.COMMENT
                or tokens[idx - 3].string != "\n"
            )

        if sys.version_info < (3, 12):
            warn(  # pragma: no cover
                "Comments extraction is currently only fully supported on Python 3.12+",
                stacklevel=2,
            )
        else:
            # get comments from all inherit fields from parent data model
            if is_typeddict(data_model):
                for base in data_model.__orig_bases__:
                    if is_typeddict(base):
                        comments.update(_get_comments(base, key_path, comments))

        # get comments from current data model
        source: str = inspect.getsource(data_model)
        # Wrap the code in a StringIO so `tokenize` can treat it like a file
        tokens = list(tokenize.generate_tokens(StringIO(source).readline))
        block_comments: list[str] = []
        inline_comment, field_name = "", ""
        for idx, tk in enumerate(tokens):
            if (
                tk.type == tokenize.NAME
                and 0 < idx < len(tokens) - 1
                and tokens[idx - 1].string != "class"
                and tokens[idx + 1].string == ":"
            ):
                if is_prev_not_block_comment(idx) and (
                    inline_comment or block_comments
                ):
                    update_comments()
                field_name = tk.string
            if tk.type == tokenize.COMMENT:
                if idx != 0 and tokens[idx - 1].string == "\n":  # block comment
                    if is_prev_not_block_comment(idx) and (
                        inline_comment or block_comments
                    ):
                        # first block comment
                        update_comments()
                    block_comments.append(tk.string.strip()[1:].strip())
                else:  # inline comment
                    assert not inline_comment, "Multiple inline comments found"
                    inline_comment = tk.string.strip()[1:].strip()
        # get comments from nested class based data models
        for name, type_def in data_model.__annotations__.items():
            if inspect.isclass(type_def) and type_def.__module__ != "builtins":
                comments.update(
                    _get_comments(type_def, extend_key_path(key_path, name), comments)
                )

        if block_comments or inline_comment:
            update_comments()

        return comments

    return _get_comments(data_model, key_path="", comments={})


KeyQuotation = Literal["single", "double", "none"]
"""The quotation style to be used for keys in a json5 object."""


class JSON5Encoder:
    """JSON5 encoder class. This encoder is used to serialize Python objects to JSON5
    strings. This class mirrors the standard library's JSONEncoder class, with the
    addition of a few extra options and features. This class will transform common data
    structures according to this table:

    | Python            | JSON          |
    |-------------------|---------------|
    | dict              | object        |
    | list, tuple       | array         |
    | str               | string        |
    | int, float        | number        |
    | True              | true          |
    | False             | false         |
    | None              | null          |

    To extend the encoder, subclass this class and override the
    [`.default()`][ujson5.JSON5Encoder.default] method, which will try to encode the
    data structures that are not supported by default. The
    [`.default()`][ujson5.JSON5Encoder.default] method should return a serializable object.
    If the [`.default()`][ujson5.JSON5Encoder.default] method is not overridden, the encoder
    will raise a JSON5EncodeError when trying to encode an unsupported object. The overridden
    [`.default()`][ujson5.JSON5Encoder.default] method should also call the parent class's
    [`.default()`][ujson5.JSON5Encoder.default] method to handle the default encoding.

    The constructor also takes in a `default` argument, which can be used to set a default
    function that will be called when trying to encode an unsupported object. This argument
    will take precedence over the overridden
    [`.default()`][ujson5.JSON5Encoder.default] method.

    !!! warning
        Comment extraction is currently only fully supported on Python 3.12+. On older
        versions, the function will still work but will not extract all comments from the
        parent data model.

    Example:
    ```python
    import ujson5


    class MyEncoder(ujson5.JSON5Encoder):
        def default(self, obj):
            if isinstance(obj, set):  # (1)!
                return list(obj)
            return super().default(obj)  # (2)!


    user = {"name": "John", "age": "123", "hobbies": {"tennis", "reading"}}
    print(ujson5.dumps(user, cls=MyEncoder))
    # {"name": "John", "age": "123", "hobbies": ["reading", "tennis"]}
    ```

    1. In this example, the encoder subclass `MyEncoder` overrides the
    [`.default()`][ujson5.JSON5Encoder.default] method to handle the serialization of sets.
    The method returns a list of the set elements.
    2. It is recommended to call the parent class's [`.default()`][ujson5.JSON5Encoder.default]
    method to handle the default encoding.

    All arguments are keyword-only arguments.

    Args:
        default: A function that returns a serializable object when trying to encode an
            unsupported object. If None, the default`.default()` method will be used.
            Defaults to None.
        skip_keys: If True, keys with unsupported types (anything other than str, int, float,
            bool, or None) will be skipped. Otherwise, an exception will be raised.
            Defaults to False.
        ensure_ascii: If True, all non-ASCII characters will be escaped. Defaults to True.
        check_circular: If True, circular references will be checked. This will introduce a
            small performance hit. Defaults to True.
        allow_nan: If True, NaN, Infinity, and -Infinity will be allowed. Otherwise, an
            exception will be raised when trying to encode these values. Defaults to True.
        indent: If not None, the output will be formatted with the given indent level.
            Otherwise, the output will be compact. Defaults to None.
        separators: A tuple containing the item separator and the key-value separator.
            Defaults to None. If None, it will be set to (", ", ": ") if indent is None,
            and (",", ":") if indent is not None.
        sort_keys: If True, the keys will be sorted. Defaults to False.
        key_quotation: The quotation style to be used for keys. Can be one of "single",
            "double", or "none". If "single" or "double", the keys will be enclosed in
            single or double quotes, respectively. If "none", the keys will not be enclosed
            in quotes. Defaults to "double".
        trailing_comma: If True, a trailing comma will be added to the last item in
            a list or dictionary. If None, a trailing comma will be added if indent
            is not None. Defaults to None.
    """

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
        key_quotation: KeyQuotation = "double",
        trailing_comma: bool | None = None,
    ) -> None:
        self._skip_keys: bool = skip_keys
        self._ensure_ascii: bool = ensure_ascii
        self._allow_nan: bool = allow_nan
        self._sort_keys: bool = sort_keys
        self._indent_str: str | None = " " * indent if indent is not None else None
        self._item_separator: str = ", "
        self._key_separator: str = ": "
        self._key_quotation: str = key_quotation
        if indent is not None:
            self._item_separator = ","
        self._trailing_comma: bool = indent is not None
        if trailing_comma is not None:
            self._trailing_comma = trailing_comma
        if separators is not None:
            self._item_separator, self._key_separator = separators

        self._default: DefaultInterface | None = default

        if check_circular:
            self._markers: dict[int, Any] | None = {}
        else:
            self._markers = None

        self._comments_cache: CommentsCache = {}

    def _is_valid_data_model(self, data_model: Any) -> bool:
        """Check if the data model is a user defined class

        Args:
            data_model: A class based data model (e.g. TypedDict, dataclass, etc.)

        Returns:
            bool: True if the data model is a user defined class, False otherwise
        """
        if data_model is None:
            return True
        return inspect.isclass(data_model) and data_model.__module__ != "builtins"

    def encode(self, obj: Any, data_model: Any | None = None) -> str:
        """Return a JSON5 string representation of a Python object.

        Args:
            obj: The Python object to be serialized
            data_model: A class based data model (e.g. TypedDict, dataclass, etc.) that
                will be used to extract comments. Defaults to None.

        Returns:
            str: The JSON5 string representation of the Python object

        Raises:
            JSON5EncodeError: If the data model class is not a user defined class or if the
                object cannot be serialized
        """
        if not self._is_valid_data_model(data_model):
            raise JSON5EncodeError(EncoderErrors.invalid_data_model(data_model))
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

        chunks = self.iterencode(obj, data_model)
        if not isinstance(chunks, (list, tuple)):
            chunks = list(chunks)
        return "".join(chunks)

    def iterencode(self, obj: Any, data_model: Any | None = None) -> Iterable[str]:
        """Encode the given object and yield each part of the JSON5 string representation

        Args:
            obj: The Python object to be serialized
            data_model: A class based data model (e.g. TypedDict, dataclass, etc.) that
                will be used to extract comments. Defaults to None.

        Returns:
            Iterable[str]: An iterable of strings representing the JSON5 serialization of the
                Python object

        Raises:
            JSON5EncodeError: If the data model class is not a user defined class or if the
                object cannot be serialized
        """
        if not self._is_valid_data_model(data_model):
            raise JSON5EncodeError(EncoderErrors.invalid_data_model(data_model))
        if data_model is not None and self._indent_str is not None:
            self._comments_cache = get_comments(data_model)

        return self._iterencode(obj, indent_level=0, key_path="")

    def default(self, obj: Any) -> Serializable:
        """Override this method in a subclass to implement custom serialization
        for objects that are not serializable by default. This method should return
        a serializable object. If this method is not overridden, the encoder will
        raise a JSON5EncodeError when trying to encode an unsupported object.

        Args:
            obj: The object to be serialized that is not supported by default

        Returns:
            Serializable: A serializable object

        Raises:
            JSON5EncodeError: If the object cannot be serialized
        """
        if self._default is not None:
            return self._default(obj)
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
            matched_str = match.group(0)
            try:
                return ESCAPE_DCT[matched_str]
            except KeyError:
                key: int = ord(matched_str)
                if key < 0x10000:
                    return f"\\u{key:04x}"
                # surrogate pair
                key -= 0x10000
                s1 = 0xD800 | ((key >> 10) & 0x3FF)
                s2 = 0xDC00 | (key & 0x3FF)
                return f"\\u{s1:04x}\\u{s2:04x}"

        if self._ensure_ascii:
            raw_str: str = ESCAPE_ASCII.sub(replace_ascii, obj)
        else:
            raw_str = ESCAPE.sub(replace_unicode, obj)
        if not key_str:
            return f'"{raw_str}"'
        if self._key_quotation == "none":
            return raw_str
        if self._key_quotation == "single":
            return f"'{raw_str}'"
        assert self._key_quotation == "double", self._key_quotation
        return f'"{raw_str}"'

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

            if idx != total_items - 1 or self._trailing_comma:
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
    key_quotation="double",
    trailing_comma=None,
)


def dumps(
    obj: Any,
    data_model: Any | None = None,
    *,
    cls: type[JSON5Encoder] | None = None,
    default: DefaultInterface | None = None,
    skip_keys: bool = False,
    ensure_ascii: bool = True,
    check_circular: bool = True,
    allow_nan: bool = True,
    indent: int | None = None,
    separators: tuple[str, str] | None = None,
    sort_keys: bool = False,
    key_quotation: KeyQuotation = "double",
    trailing_comma: bool | None = None,
) -> str:
    """Serialize `obj` to a JSON5 formatted `str`.

    Example:
    ```python
    import ujson5
    user = {"name": "John", "age": 123, "hobbies": ["tennis", "reading"]}
    print(ujson5.dumps(user))
    # Output: '{"name": "John", "age": 123, "hobbies": ["tennis", "reading"]}'
    ```

    All arguments except `obj` and `data_model` are keyword-only arguments.

    Args:
        cls: The encoder class to be used. a custom [`JSON5Encoder`][ujson5.JSON5Encoder]
            subclass (e.g. one that overrides the [`.default()`][ujson5.JSON5Encoder.default]
            method to serialize additional types) can be provided. If None, the default
            [`JSON5Encoder`][ujson5.JSON5Encoder] class will be used. Defaults to None.
        default: A function that returns a serializable object when trying to encode an
            unsupported object. If None, the default
            [`.default()`][ujson5.JSON5Encoder.default] method will be used. Defaults to None.
        skip_keys: If True, keys with unsupported types (anything other than str, int, float,
            bool, or None) will be skipped. Otherwise, an exception will be raised.
            Defaults to False.
        ensure_ascii: If True, all non-ASCII characters will be escaped. Defaults to True.
        check_circular: If True, circular references will be checked. This will introduce a
            small performance hit. Defaults to True.
        allow_nan: If True, NaN, Infinity, and -Infinity will be allowed. Otherwise, an
            exception will be raised when trying to encode these values. Defaults to True.
        indent: If not None, the output will be formatted with the given indent level.
            Otherwise, the output will be compact. Defaults to None.
        separators: A tuple containing the item separator and the key-value separator.
            Defaults to None. If None, it will be set to (", ", ": ") if indent is None,
            and (",", ":") if indent is not None.
        sort_keys: If True, the keys will be sorted. Defaults to False.
        key_quotation: The quotation style to be used for keys. Can be one of "single",
            "double", or "none". If "single" or "double", the keys will be enclosed in
            single or double quotes, respectively. If "none", the keys will not be enclosed
            in quotes. Defaults to "double".
        trailing_comma: If True, a trailing comma will be added to the last item in
            a list or dictionary. If None, a trailing comma will be added if indent
            is not None. Defaults to None.

    Returns:
        str: The JSON5 formatted string representation of the Python object

    Raises:
        JSON5EncodeError: If the object cannot be serialized
    """
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
        and key_quotation == "double"
        and trailing_comma is None
    ):
        return _default_encoder.encode(obj, data_model)
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
        key_quotation=key_quotation,
        trailing_comma=trailing_comma,
    ).encode(obj, data_model)


def dump(
    obj: Any,
    fp: TextIO,
    data_model: Any | None = None,
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
    key_quotation: KeyQuotation = "double",
    trailing_comma: bool | None = None,
) -> None:
    """Serialize `obj` as a JSON formatted stream to `fp` (a `.write()`-supporting
    file-like object).

    Example:
    ```python
    import ujson5
    user = {"name": "John", "age": 123, "hobbies": ["tennis", "reading"]}
    with open("user.json", "w") as f:
        ujson5.dump(user, f)
    ```

    Args:
        cls: The encoder class to be used. a custom [`JSON5Encoder`][ujson5.JSON5Encoder]
            subclass (e.g. one that overrides the [`.default()`][ujson5.JSON5Encoder.default]
            method to serialize additional types) can be provided. If None, the default
            [`JSON5Encoder`][ujson5.JSON5Encoder] class will be used. Defaults to None.
        default: A function that returns a serializable object when trying to encode an
            unsupported object. If None, the default
            [`.default()`][ujson5.JSON5Encoder.default] method will be used. Defaults to None.
        skip_keys: If True, keys with unsupported types (anything other than str, int, float,
            bool, or None) will be skipped. Otherwise, an exception will be raised.
            Defaults to False.
        ensure_ascii: If True, all non-ASCII characters will be escaped. Defaults to True.
        check_circular: If True, circular references will be checked. This will introduce a
            small performance hit. Defaults to True.
        allow_nan: If True, NaN, Infinity, and -Infinity will be allowed. Otherwise, an
            exception will be raised when trying to encode these values. Defaults to True.
        indent: If not None, the output will be formatted with the given indent level.
            Otherwise, the output will be compact. Defaults to None.
        separators: A tuple containing the item separator and the key-value separator.
            Defaults to None. If None, it will be set to (", ", ": ") if indent is None,
            and (",", ":") if indent is not None.
        sort_keys: If True, the keys will be sorted. Defaults to False.
        key_quotation: The quotation style to be used for keys. Can be one of "single",
            "double", or "none". If "single" or "double", the keys will be enclosed in
            single or double quotes, respectively. If "none", the keys will not be enclosed
            in quotes. Defaults to "double".
        trailing_comma: If True, a trailing comma will be added to the last item in
            a list or dictionary. If None, a trailing comma will be added if indent
            is not None. Defaults to None.

    Returns:
        str: The JSON5 formatted string representation of the Python object

    Raises:
        JSON5EncodeError: If the object cannot be serialized
    """
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
        and key_quotation == "double"
        and trailing_comma is None
    ):
        iterable = _default_encoder.iterencode(obj, data_model)
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
            key_quotation=key_quotation,
            trailing_comma=trailing_comma,
        ).iterencode(obj, data_model)
    for chunk in iterable:
        fp.write(chunk)
    fp.write("\n")
