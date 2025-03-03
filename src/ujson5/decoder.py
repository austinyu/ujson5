"""Implementation of the JSON5 decoder."""

from collections.abc import Callable
import re
from typing import Any, Literal, TextIO

from .core import (
    JsonValue,
    JsonValuePairs,
    JSON5DecodeError,
    Token,
    TOKEN_TYPE,
)
from .consts import ESCAPE_SEQUENCE, RESERVED_WORDS
from .err_msg import DecoderErr
from .lexer import tokenize

ObjectHookArg = dict[str, JsonValue]
"""Type hint for the argument of the `object_hook` function."""
ObjectHook = Callable[[ObjectHookArg], Any]
"""Type hint for the `object_hook` function signature."""
ObjectPairsHookArg = list[tuple[str, JsonValue]]
"""Type hint for the argument of the `object_pairs_hook` function."""
ObjectPairsHook = Callable[[ObjectPairsHookArg], Any]
"""Type hint for the `object_pairs_hook` function signature."""


class Json5Decoder:
    """JSON5 decoder

    Performs the following translations in decoding by default:

    | JSON          | Python            |
    |---------------|-------------------|
    | object        | dict              |
    | array         | list              |
    | string        | str               |
    | number (int)  | int               |
    | number (real) | float             |
    | true          | True              |
    | false         | False             |
    | null          | None              |

    It also understands `NaN`, `Infinity`, and `-Infinity` as
    their corresponding `float` values, which is outside the JSON spec.

    Example:
    ```python
    import ujson5
    json5_str = '{"key": "value"}'
    obj = ujson5.Json5Decoder().decode(json5_str)
    # obj == {'key': 'value'}
    ```

    Args:
        parse_float: if specified, will be called with the string of every JSON float to be
            decoded. By default this is equivalent to float(num_str). This can be used to use
            another datatype or parser for JSON floats (e.g. decimal.Decimal).
        parse_int: if specified, will be called with the string of every JSON int to be
            decoded. By default this is equivalent to int(num_str). This can be used to
            use another datatype or parser for JSON integers (e.g. float).
        parse_constant: if specified, will be called with one of the following strings:
            -Infinity, Infinity, NaN. This can be used to raise an exception if invalid
            JSON numbers are encountered.
        strict: control characters will be allowed inside strings if `strict` is False.
            Control characters in this context are those with character codes in the 0-31
            range, including `'\\t'` (tab), `'\\n'`, `'\\r'` and `'\\0'`.
        allow_reserved_words: if `True`, reserved words can be used as identifiers. Reserved
            words are defined here https://262.ecma-international.org/5.1/#sec-7.6.1.
            Default is `True`.
        object_hook: an optional function that will be called with the result of any object
            literal decode (a `dict`). The return value of `object_hook` will be used instead
            of the `dict`. This feature can be used to implement custom decoders
            (e.g. JSON-RPC class hinting).
        object_pairs_hook: if specified will be called with the result of every JSON object
            decoded with an ordered list of pairs.  The return value of `object_pairs_hook`
            will be used instead of the `dict`. This feature can be used to implement
            custom decoders. If `object_hook` is also defined, the `object_pairs_hook`
            takes priority.

    Raises:
        JSON5DecodeError: If the JSON5 string is invalid.
    """

    def __init__(
        self,
        *,
        parse_float: Callable[[str], Any] | None = None,
        parse_int: Callable[[str], Any] | None = None,
        parse_constant: Callable[[str], Any] | None = None,
        strict: bool = True,
        allow_reserved_words: bool = True,
        object_hook: ObjectHook | None = None,
        object_pairs_hook: ObjectPairsHook | None = None,
    ) -> None:
        self._object_hook: ObjectHook | None = object_hook
        self._parse_float: Callable[[str], Any] | None = parse_float
        self._parse_int: Callable[[str], Any] | None = parse_int
        self._parse_constant: Callable[[str], Any] | None = parse_constant
        self._allow_reserved_words: bool = allow_reserved_words
        self._strict: bool = strict
        self._object_pairs_hook: ObjectPairsHook | None = object_pairs_hook

    def decode(self, json5_str: str) -> Any:
        """Deserialize a JSON5 string to a Python object.

        Args:
            json5_str: The JSON5 string to be deserialized.

        Returns:
            The Python object represented by the JSON5 string.

        Raises:
            JSON5DecodeError: If the JSON5 string is invalid.
        """
        tokens = tokenize(json5_str)
        return self._parse_json5(json5_str, tokens)

    def raw_decode(self, json5_str: str) -> tuple[Any, int]:
        """Deserialize a JSON5 string to a Python object and return the index of the last
        character parsed.

        Args:
            json5_str: The JSON5 string to be deserialized.

        Returns:
            A tuple of the Python object represented by the JSON5 string and the index
                of the last character parsed.

        Raises:
            JSON5DecodeError: If the JSON5 string is invalid.
        """
        tokens = tokenize(json5_str)
        if tokens[-1].tk_type == TOKEN_TYPE["STRING"]:
            # If the last token is a string, we need to skip the closing quote
            return self._parse_json5(json5_str, tokens), tokens[-1].value[1] + 1
        return self._parse_json5(json5_str, tokens), tokens[-1].value[1]

    def _parse_json5(
        self, json5_str: str, tokens: list[Token]
    ) -> JsonValue | JsonValuePairs:
        """Parse a JSON5 string with tokens."""
        if not tokens:
            raise JSON5DecodeError(DecoderErr.empty_json5(), json5_str, 0)

        # stack contains (type, data, last_key) tuples
        stack: list[tuple[Literal["object", "array"], JsonValue, str | None]] = []
        root: JsonValue | JsonValuePairs = None
        root_defined: bool = False

        # A helper function to add a new value to the top of the stack
        def add_value_to_top(value: JsonValue, local_idx: int) -> JsonValue | None:
            # If stack is empty, this is the root value
            if not stack:
                return value

            top_type, top_data, top_last_key = stack[-1]
            if top_type == "object":
                if top_last_key is None:
                    # We didn't expect a value without a key
                    raise JSON5DecodeError(
                        DecoderErr.expecting_property_name(), json5_str, 0
                    )
                # Insert into dict under the key
                if self._object_pairs_hook is not None:
                    assert isinstance(top_data, list)
                    top_data.append((top_last_key, value))
                else:
                    assert isinstance(top_data, dict)
                    top_data[top_last_key] = value
                # Reset last_key
                stack[-1] = (top_type, top_data, None)
            else:  # array
                assert top_type == "array"
                assert isinstance(top_data, list)
                if tokens[local_idx - 1].tk_type not in {
                    TOKEN_TYPE["PUN_COMMA"],
                    TOKEN_TYPE["PUN_OPEN_BRACKET"],
                }:
                    # it is not the first element and the comma is missing
                    raise JSON5DecodeError(
                        DecoderErr.missing_comma("array"),
                        json5_str,
                        tokens[local_idx].value[0],
                    )
                top_data.append(value)
            return None  # The root remains unchanged unless stack was empty

        def update_root(new_root: JsonValue, root_start: int) -> None:
            nonlocal root, root_defined
            if root_defined:
                raise JSON5DecodeError(
                    DecoderErr.multiple_root(), json5_str, root_start
                )
            root = new_root
            root_defined = True

        def update_last_key(new_key: str, local_idx: int) -> None:
            if (
                local_idx + 1 >= len(tokens)
                or tokens[local_idx + 1].tk_type != TOKEN_TYPE["PUN_COLON"]
            ):
                # key should always be followed by a colon
                raise JSON5DecodeError(
                    DecoderErr.missing_colon(),
                    json5_str,
                    tokens[local_idx].value[0],
                )
            if tokens[local_idx - 1].tk_type not in {
                TOKEN_TYPE["PUN_COMMA"],
                TOKEN_TYPE["PUN_OPEN_BRACE"],
            }:
                # it is not the first key-value pair and the comma is missing
                raise JSON5DecodeError(
                    DecoderErr.missing_comma("array"),
                    json5_str,
                    tokens[local_idx].value[0],
                )
            top_type, top_data, _ = stack[-1]
            stack[-1] = (top_type, top_data, new_key)

        idx = 0
        while idx < len(tokens):
            tk_start, tk_typ = tokens[idx].value[0], tokens[idx].tk_type
            tk_str = json5_str[tokens[idx].value[0] : tokens[idx].value[1]]

            if tk_typ == TOKEN_TYPE["PUN_OPEN_BRACE"]:
                if self._object_pairs_hook is not None:
                    new_obj: list[tuple[str, JsonValue]] | dict[str, JsonValue] = []
                else:
                    new_obj = {}
                add_value_to_top(new_obj, idx)
                # Push onto the stack
                stack.append(("object", new_obj, None))

            elif tk_typ == TOKEN_TYPE["PUN_CLOSE_BRACE"]:
                if not stack or stack[-1][0] != "object":
                    raise JSON5DecodeError(
                        DecoderErr.unexpected_punctuation("}"), json5_str, tk_start
                    )
                top_layer = stack.pop()
                if not stack:
                    # If stack is now empty, that means this object is the root
                    update_root(top_layer[1], tk_start)

            elif tk_typ == TOKEN_TYPE["PUN_OPEN_BRACKET"]:
                new_arr: list[JsonValue] = []
                add_value_to_top(new_arr, idx)
                stack.append(("array", new_arr, None))

            elif tk_typ == TOKEN_TYPE["PUN_CLOSE_BRACKET"]:
                if not stack or stack[-1][0] != "array":
                    raise JSON5DecodeError(
                        DecoderErr.unexpected_punctuation("]"), json5_str, tk_start
                    )
                top_layer = stack.pop()
                if not stack:
                    # If stack is now empty, that means this array is the root
                    update_root(top_layer[1], tk_start)

            elif tk_typ == TOKEN_TYPE["IDENTIFIER"]:
                if not stack or stack[-1][0] == "array" or stack[-1][2] is not None:
                    # identifier can only be used as a key in an object
                    raise JSON5DecodeError(
                        DecoderErr.unexpected_identifier(), json5_str, tk_start
                    )
                if not self._allow_reserved_words and tk_str in RESERVED_WORDS:
                    raise JSON5DecodeError(
                        DecoderErr.reserved_word(tk_str), json5_str, tk_start
                    )
                update_last_key(self._parse_identifier(tk_str), idx)
            elif tk_typ == TOKEN_TYPE["STRING"]:
                parsed_str = self._parse_string(tk_str, json5_str, tk_start)
                if not stack:
                    # A bare string is a root-level scalar
                    update_root(parsed_str, tk_start)
                else:
                    top_type, _, top_last_key = stack[-1]
                    if top_type == "object":
                        # If last_key is None, this string should be a key
                        if top_last_key is None:
                            update_last_key(parsed_str, idx)
                        else:
                            # last_key is already set, so this string is a value
                            add_value_to_top(parsed_str, idx)
                    else:
                        # top_type is array
                        add_value_to_top(parsed_str, idx)

            elif tk_typ == TOKEN_TYPE["NUMBER"]:
                parsed_number = self._parse_number(tk_str)
                # These are scalar values
                if not stack:
                    # A bare scalar is root-level
                    update_root(parsed_number, tk_start)
                else:
                    add_value_to_top(parsed_number, idx)

            elif tk_typ == TOKEN_TYPE["BOOLEAN"]:
                assert tk_str in {"true", "false"}
                parsed_bool = tk_str == "true"
                if not stack:
                    update_root(parsed_bool, tk_start)
                else:
                    add_value_to_top(parsed_bool, idx)

            elif tk_typ == TOKEN_TYPE["NULL"]:
                assert tk_str == "null"
                if not stack:
                    update_root(None, tk_start)
                else:
                    add_value_to_top(None, idx)

            elif tk_typ == TOKEN_TYPE["PUN_COLON"]:
                # Just validate that we are in an object and have a last_key
                if not stack:
                    raise JSON5DecodeError(
                        DecoderErr.expecting_value(), json5_str, tk_start
                    )
                top_type, _, top_last_key = stack[-1]
                # Colon should only be used in an object and after a key
                if top_type != "object":
                    raise JSON5DecodeError(
                        DecoderErr.unexpected_colon_in_array(), json5_str, tk_start
                    )
                if top_last_key is None:
                    raise JSON5DecodeError(
                        DecoderErr.missing_key_with_colon(), json5_str, tk_start
                    )
                if idx + 1 >= len(tokens):
                    raise JSON5DecodeError(
                        DecoderErr.unexpected_eof(), json5_str, tk_start
                    )
                if tokens[idx + 1].tk_type in {
                    TOKEN_TYPE["PUN_CLOSE_BRACE"],
                    TOKEN_TYPE["PUN_CLOSE_BRACKET"],
                    TOKEN_TYPE["PUN_COMMA"],
                    TOKEN_TYPE["PUN_COLON"],
                }:
                    raise JSON5DecodeError(
                        DecoderErr.unexpected_punctuation(
                            json5_str[tokens[idx + 1].value[0]]
                        ),
                        json5_str,
                        tokens[idx + 1].value[0],
                    )

            else:
                assert tk_typ == TOKEN_TYPE["PUN_COMMA"]
                if idx + 1 >= len(tokens) or idx == 0:
                    raise JSON5DecodeError(
                        DecoderErr.expecting_value(), json5_str, tk_start
                    )
                if not stack:
                    raise JSON5DecodeError(
                        DecoderErr.unexpected_punctuation(","), json5_str, tk_start
                    )
                if stack[-1][0] == "object":
                    # in an object, anything before a comma should be a value
                    if tokens[idx - 1].tk_type not in {
                        TOKEN_TYPE["STRING"],
                        TOKEN_TYPE["NUMBER"],
                        TOKEN_TYPE["BOOLEAN"],
                        TOKEN_TYPE["NULL"],
                        TOKEN_TYPE["PUN_CLOSE_BRACE"],
                        TOKEN_TYPE["PUN_CLOSE_BRACKET"],
                    }:
                        raise JSON5DecodeError(
                            DecoderErr.expecting_property_value(
                                tokens[idx - 1].tk_type
                            ),
                            json5_str,
                            tk_start,
                        )
                    # in an object, anything after a comma should be a key
                    # or the end of the object
                    if tokens[idx + 1].tk_type not in {
                        TOKEN_TYPE["STRING"],
                        TOKEN_TYPE["IDENTIFIER"],
                        TOKEN_TYPE["PUN_CLOSE_BRACE"],
                    }:
                        raise JSON5DecodeError(
                            DecoderErr.expecting_property_name(tokens[idx + 1].tk_type),
                            json5_str,
                            tokens[idx + 1].value[0],
                        )
                elif stack[-1][0] == "array":
                    # in an array, anything before a comma should be a value
                    if tokens[idx - 1].tk_type not in {
                        TOKEN_TYPE["STRING"],
                        TOKEN_TYPE["NUMBER"],
                        TOKEN_TYPE["BOOLEAN"],
                        TOKEN_TYPE["NULL"],
                        TOKEN_TYPE["PUN_CLOSE_BRACE"],
                        TOKEN_TYPE["PUN_CLOSE_BRACKET"],
                    }:
                        raise JSON5DecodeError(
                            DecoderErr.expecting_value(), json5_str, tk_start
                        )
                    # in an array, anything after a comma should be a value
                    # or the end of the array
                    if tokens[idx + 1].tk_type not in {
                        TOKEN_TYPE["STRING"],
                        TOKEN_TYPE["NUMBER"],
                        TOKEN_TYPE["BOOLEAN"],
                        TOKEN_TYPE["NULL"],
                        TOKEN_TYPE["PUN_CLOSE_BRACKET"],
                        TOKEN_TYPE["PUN_OPEN_BRACKET"],
                        TOKEN_TYPE["PUN_OPEN_BRACE"],
                    }:
                        raise JSON5DecodeError(
                            DecoderErr.expecting_value(), json5_str, tk_start
                        )
            idx += 1

        # If everything is parsed, the stack should be empty (all objects/arrays closed)
        if stack:
            raise JSON5DecodeError(
                DecoderErr.expecting_value(), json5_str, tokens[-1].value[0]
            )

        if self._object_pairs_hook is None and self._object_hook is not None:
            try:
                return self._object_hook(root) if isinstance(root, dict) else root
            except Exception as e:
                raise JSON5DecodeError(
                    DecoderErr.invalid_object_hook(), json5_str, tokens[-1].value[0]
                ) from e
        if self._object_pairs_hook is not None:
            try:
                return self._object_pairs_hook(root)  # type: ignore
            except Exception as e:
                raise JSON5DecodeError(
                    DecoderErr.invalid_object_pairs_hook(),
                    json5_str,
                    tokens[-1].value[0],
                ) from e

        # no hooks provided, just parse the JSON5 string
        return root

    def _parse_number(self, num_str: str) -> int | float:
        """Parse a number."""
        if "Infinity" in num_str:
            return (
                float("-inf" if "-" in num_str else "inf")
                if self._parse_constant is None
                else self._parse_constant(num_str)
            )
        if "NaN" in num_str:
            return (
                float("-nan" if "-" in num_str else "nan")
                if self._parse_constant is None
                else self._parse_constant(num_str)
            )
        if "0x" in num_str or "0X" in num_str:
            return int(num_str, 16)
        if "." in num_str or "e" in num_str or "E" in num_str:
            return (
                float(num_str)
                if self._parse_float is None
                else self._parse_float(num_str)
            )
        return int(num_str) if self._parse_int is None else self._parse_int(num_str)

    def _parse_string(self, str_str: str, json5_str: str, str_start_idx: int) -> str:
        def replace_escape_sequences_and_continuations(match):
            """Unescape escape sequences, unicode escape sequence
                and line continuations in a string.
            escape sequences replaced: `\'`, `\"`, `\\`, `\b`, `\f`, `\n`, `\r`, `\t`,
                `\v`, `\0`
            unicode escape sequences replaced: `\\u` followed by 4 hexadecimal digits
            line continuations replaced: `\\` followed by a newline character
            """
            if match.group(1):
                # in strict mode, control characters are not allowed
                if self._strict and match.group(1) in {"t", "n", "r", "0"}:
                    raise JSON5DecodeError(
                        DecoderErr.invalid_control_char(),
                        json5_str,
                        str_start_idx + match.start(),
                    )
                return ESCAPE_SEQUENCE[match.group(1)]
            if match.group(2):
                return chr(int(match.group(2), 16))
            return ""

        # group 1: escape sequences, group 2: unicode escape sequences
        # group 3: line continuations
        return re.sub(
            r"\\([\'\"\\bfnrtv0])|\\u([0-9a-fA-F]{4})|\\\s*\n",
            replace_escape_sequences_and_continuations,
            str_str,
        )

    def _parse_identifier(self, id_str: str) -> str:
        def replace_unicode_escape_sequences(match):
            """Unescape unicode escape sequences in an identifier.
            unicode escape sequences replaced: `\\u` followed by 4 hexadecimal digits
            """
            return chr(int(match.group(1), 16))

        # group 1: escape sequences, group 2: unicode escape sequences
        # group 3: line continuations
        return re.sub(
            r"\\u([0-9a-fA-F]{4})",
            replace_unicode_escape_sequences,
            id_str,
        )


def loads(
    json5_str: str,
    *,
    cls: type[Json5Decoder] | None = None,
    parse_float: Callable[[str], Any] | None = None,
    parse_int: Callable[[str], Any] | None = None,
    parse_constant: Callable[[str], Any] | None = None,
    strict: bool = True,
    allow_reserved_words: bool = True,
    object_hook: ObjectHook | None = None,
    object_pairs_hook: ObjectPairsHook | None = None,
) -> Any:
    """Deserialize `json5_str` (a `str`, `bytes` or `bytearray` instance
    containing a JSON document) to a Python object.

    Example:
    ```python
    import ujson5
    json5_str = '{"key": "value"}'
    obj = ujson5.loads(json5_str)
    # obj == {'key': 'value'}
    ```

    All arguments except `json5_str` are keyword-only.

    Args:
        json5_str: The JSON5 string to be deserialized.
        cls: If specified, must be a [`Json5Decoder`][ujson5.Json5Decoder] subclass. The `cls`
            will be used to instantiate the decoder. If `cls` is not specified, the default
            `Json5Decoder` will be used.
        parse_float: if specified, will be called with the string of every JSON float to be
            decoded. By default this is equivalent to float(num_str). This can be used to use
            another datatype or parser for JSON floats (e.g. decimal.Decimal).
        parse_int: if specified, will be called with the string of every JSON int to be
            decoded. By default this is equivalent to int(num_str). This can be used to
            use another datatype or parser for JSON integers (e.g. float).
        parse_constant: if specified, will be called with one of the following strings:
            '-Infinity', 'Infinity', 'NaN'. This can be used to raise an exception if invalid
            JSON numbers are encountered.
        strict: control characters will be allowed inside strings if `strict` is False.
            Control characters in this context are those with character codes in the 0-31
            range, including `'\\t'` (tab), `'\\n'`, `'\\r'` and `'\\0'`.
        allow_reserved_words: if `True`, reserved words can be used as identifiers. Reserved
            words are defined here https://262.ecma-international.org/5.1/#sec-7.6.1.
            Default is `True`.
        object_hook: an optional function that will be called with the result of any object
            literal decode (a `dict`). The return value of `object_hook` will be used instead
            of the `dict`. This feature can be used to implement custom decoders
            (e.g. JSON-RPC class hinting).
        object_pairs_hook: if specified will be called with the result of every JSON object
            decoded with an ordered list of pairs.  The return value of `object_pairs_hook`
            will be used instead of the `dict`. This feature can be used to implement
            custom decoders. If `object_hook` is also defined, the `object_pairs_hook`
            takes priority.
    """
    if cls is not None:
        decoder: Json5Decoder = cls(
            object_hook=object_hook,
            parse_float=parse_float,
            parse_int=parse_int,
            parse_constant=parse_constant,
            strict=strict,
            allow_reserved_words=allow_reserved_words,
            object_pairs_hook=object_pairs_hook,
        )
    else:
        decoder = Json5Decoder(
            object_hook=object_hook,
            parse_float=parse_float,
            parse_int=parse_int,
            parse_constant=parse_constant,
            strict=strict,
            allow_reserved_words=allow_reserved_words,
            object_pairs_hook=object_pairs_hook,
        )
    return decoder.decode(json5_str)


def load(
    file: TextIO,
    *,
    cls: type[Json5Decoder] | None = None,
    parse_float: Callable[[str], Any] | None = None,
    parse_int: Callable[[str], Any] | None = None,
    parse_constant: Callable[[str], Any] | None = None,
    strict: bool = True,
    allow_reserved_words: bool = True,
    object_hook: ObjectHook | None = None,
    object_pairs_hook: ObjectPairsHook | None = None,
) -> Any:
    """Deserialize `fp` (a `.read()`-supporting file-like object containing
    a JSON document) to a Python object.

    Example:
    ```python
    import ujson5
    with open('file.json5', 'r') as f:
        obj = ujson5.load(f)
    ```

    All arguments except `file` are keyword-only.

    Args:
        file: A file-like object containing a JSON document.
        cls: If specified, must be a [`Json5Decoder`][ujson5.Json5Decoder] subclass. The `cls`
            will be used to instantiate the decoder. If `cls` is not specified, the default
            `Json5Decoder` will be used.
        parse_float: if specified, will be called with the string of every JSON float to be
            decoded. By default this is equivalent to float(num_str). This can be used to use
            another datatype or parser for JSON floats (e.g. decimal.Decimal).
        parse_int: if specified, will be called with the string of every JSON int to be
            decoded. By default this is equivalent to int(num_str). This can be used to
            use another datatype or parser for JSON integers (e.g. float).
        parse_constant: if specified, will be called with one of the following strings:
            -Infinity, Infinity, NaN. This can be used to raise an exception if invalid
            JSON numbers are encountered.
        strict: control characters will be allowed inside strings if `strict` is False.
            Control characters in this context are those with character codes in the 0-31
            range, including `'\\t'` (tab), `'\\n'`, `'\\r'` and `'\\0'`.
        allow_reserved_words: if `True`, reserved words can be used as identifiers. Reserved
            words are defined here https://262.ecma-international.org/5.1/#sec-7.6.1.
            Default is `True`.
        object_hook: an optional function that will be called with the result of any object
            literal decode (a `dict`). The return value of `object_hook` will be used instead
            of the `dict`. This feature can be used to implement custom decoders
            (e.g. JSON-RPC class hinting).
        object_pairs_hook: if specified will be called with the result of every JSON object
            decoded with an ordered list of pairs.  The return value of `object_pairs_hook`
            will be used instead of the `dict`. This feature can be used to implement
            custom decoders. If `object_hook` is also defined, the `object_pairs_hook`
            takes priority.
    """
    return loads(
        file.read(),
        cls=cls,
        object_hook=object_hook,
        parse_float=parse_float,
        parse_int=parse_int,
        parse_constant=parse_constant,
        strict=strict,
        allow_reserved_words=allow_reserved_words,
        object_pairs_hook=object_pairs_hook,
    )
