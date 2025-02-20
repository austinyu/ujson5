"""TODO"""

from collections.abc import Callable
import re
from typing import Any, Literal, TextIO

from .core import JsonValue, JsonValuePairs, JSON5DecodeError, Token, TokenType
from .consts import ESCAPE_SEQUENCE
from .err_msg import ParseErrors
from .lexer import tokenize


class Json5Decoder:
    """TODO"""

    def __init__(
        self,
        *,
        object_hook: Callable[[dict[str, JsonValue]], Any] | None = None,
        parse_float: Callable[[str], Any] | None = None,
        parse_int: Callable[[str], Any] | None = None,
        parse_constant: Callable[[str], Any] | None = None,
        strict: bool = True,
        object_pairs_hook: Callable[[tuple[str, JsonValue]], Any] | None = None,
    ) -> None:
        self._object_hook: Callable[[dict[str, JsonValue]], Any] | None = object_hook
        self._parse_float: Callable[[str], Any] | None = parse_float
        self._parse_int: Callable[[str], Any] | None = parse_int
        self._parse_constant: Callable[[str], Any] | None = parse_constant
        self._strict: bool = strict
        self._object_pairs_hook: Callable[[tuple[str, JsonValue]], Any] | None = (
            object_pairs_hook
        )

    def decode(self, json5_str: str) -> Any:
        """TODO"""
        tokens = tokenize(json5_str)
        return self._parse_json5(json5_str, tokens)

    def raw_decode(self, json5_str: str) -> tuple[Any, int]:
        """TODO"""
        tokens = tokenize(json5_str)
        return self._parse_json5(json5_str, tokens), tokens[-1].value[1]

    def _parse_json5(
        self, json5_str: str, tokens: list[Token]
    ) -> JsonValue | JsonValuePairs:
        """Parse a JSON5 string with tokens."""
        # stack contains (type, data, last_key) tuples
        stack: list[tuple[Literal["object", "array"], JsonValue, str | None]] = []
        root: JsonValue | JsonValuePairs = None
        root_defined: bool = False

        # A helper function to add a new value to the top of the stack
        def add_value_to_top(value: JsonValue) -> JsonValue | None:
            # If stack is empty, this is the root value
            if not stack:
                return value

            top_type, top_data, top_last_key = stack[-1]
            if top_type == "object":
                if top_last_key is None:
                    # We didn't expect a value without a key
                    raise JSON5DecodeError(
                        ParseErrors.expecting_property_name(), json5_str, 0
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
                top_data.append(value)
            return None  # The root remains unchanged unless stack was empty

        def update_root(new_root: JsonValue) -> None:
            nonlocal root, root_defined
            if root_defined:
                raise JSON5DecodeError(ParseErrors.multiple_root(), json5_str, 0)
            root = new_root
            root_defined = True

        idx = 0
        while idx < len(tokens):
            # tok = tokens[idx]
            tk_start, tk_typ = tokens[idx].value[0], tokens[idx].tk_type
            tk_str = json5_str[tokens[idx].value[0] : tokens[idx].value[1]]

            if tk_typ == TokenType.PUNCTUATOR and tk_str == "{":
                if self._object_pairs_hook is not None:
                    new_obj: list[tuple[str, JsonValue]] | dict[str, JsonValue] = []
                else:
                    new_obj = {}
                add_value_to_top(new_obj)
                # Push onto the stack
                stack.append(("object", new_obj, None))

            elif tk_typ == TokenType.PUNCTUATOR and tk_str == "}":
                if not stack or stack[-1][0] != "object":
                    raise JSON5DecodeError(
                        ParseErrors.unexpected_punctuation("}"), json5_str, tk_start
                    )
                top_layer = stack.pop()
                if not stack:
                    # If stack is now empty, that means this object is the root
                    update_root(top_layer[1])

            elif tk_typ == TokenType.PUNCTUATOR and tk_str == "[":
                new_arr: list[JsonValue] = []
                add_value_to_top(new_arr)
                stack.append(("array", new_arr, None))

            elif tk_typ == TokenType.PUNCTUATOR and tk_str == "]":
                if not stack or stack[-1][0] != "array":
                    raise JSON5DecodeError(
                        ParseErrors.unexpected_punctuation("]"), json5_str, tk_start
                    )
                top_layer = stack.pop()
                if not stack:
                    # If stack is now empty, that means this array is the root
                    update_root(top_layer[1])

            elif tk_typ == TokenType.IDENTIFIER:
                if not stack or stack[-1][0] == "array" or stack[-1][2] is not None:
                    # identifier can only be used as a key in an object
                    raise JSON5DecodeError(ParseErrors.expecting_value(), json5_str, 0)
                stack[-1] = (stack[-1][0], stack[-1][1], tk_str)
            elif tk_typ == TokenType.STRING:
                if not self._validate_line_continuation(tk_str):
                    raise JSON5DecodeError(
                        ParseErrors.bad_string_continuation(), json5_str, tk_start
                    )
                parsed_str = self._parse_string(tk_str, json5_str, tk_start)
                if not stack:
                    # A bare string is a root-level scalar
                    update_root(parsed_str)
                else:
                    top_type, top_data, top_last_key = stack[-1]
                    if top_type == "object":
                        # If last_key is None, this string should be a key
                        if top_last_key is None:
                            # Next token should be COLON
                            # We'll just store it as last_key for now
                            stack[-1] = (top_type, top_data, parsed_str)
                        else:
                            # last_key is already set, so this string is a value
                            add_value_to_top(parsed_str)
                    else:
                        # top_type is array
                        add_value_to_top(parsed_str)

            elif tk_typ == TokenType.NUMBER:
                parsed_number = self._parse_number(tk_str)
                # These are scalar values
                if not stack:
                    # A bare scalar is root-level
                    update_root(parsed_number)
                else:
                    add_value_to_top(parsed_number)

            elif tk_typ == TokenType.BOOLEAN:
                assert tk_str in {"true", "false"}
                parsed_bool = tk_str == "true"
                if not stack:
                    update_root(parsed_bool)
                else:
                    add_value_to_top(parsed_bool)

            elif tk_typ == TokenType.NULL:
                assert tk_str == "null"
                if not stack:
                    update_root(None)
                else:
                    add_value_to_top(None)

            elif tk_typ == TokenType.PUNCTUATOR and tk_str == ":":
                # Just validate that we are in an object and have a last_key
                if not stack:
                    raise JSON5DecodeError(
                        ParseErrors.expecting_value(), json5_str, tk_start
                    )
                top_type, top_data, top_last_key = stack[-1]
                if top_type != "object" or top_last_key is None:
                    raise JSON5DecodeError(
                        ParseErrors.unexpected_colon(), json5_str, tk_start
                    )
                if idx + 1 >= len(tokens):
                    raise JSON5DecodeError(
                        ParseErrors.expecting_value(), json5_str, tk_start
                    )
                if tokens[idx + 1].tk_type == TokenType.PUNCTUATOR and json5_str[
                    tokens[idx + 1].value[0]
                ] in {"]", "}", ",", ":"}:
                    raise JSON5DecodeError(
                        ParseErrors.unexpected_punctuation(
                            json5_str[tokens[idx + 1].value[0]]
                        ),
                        json5_str,
                        0,
                    )

            else:
                assert tk_typ == TokenType.PUNCTUATOR and tk_str == ","
                # Typically just means "expect another key-value or value next"
                # Validate that we are inside an object or array, and that we just
                # finished a value

            idx += 1

        # If everything is parsed, the stack should be empty (all objects/arrays closed)
        if stack:
            raise JSON5DecodeError(
                ParseErrors.expecting_value(), json5_str, tokens[-1].value[0]
            )

        if self._object_pairs_hook is not None:
            try:
                return self._object_pairs_hook(root)  # type: ignore
            except TypeError:
                return root
        if self._object_hook is not None:
            return self._object_hook(root) if isinstance(root, dict) else root
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

    def _validate_line_continuation(self, str_str: str) -> bool:
        """Validate line continuation in a string. Line continuation is a `\\`
        followed by a newline character. This function returns True if `\\` is followed
        by any number of space and a new line. Otherwise, if `\\` is followed by at
        least one space and any character other than a newline, it returns False.

        Args:
            text (str): string to validate

        Returns:
            bool: True if line continuation is valid, False otherwise
        """
        if "\\" not in str_str:
            return True
        candidates = re.finditer(r"\\\s+[^\n]", str_str)
        for match in candidates:
            if not bool(re.search(r"\\\s*\n", match.group())):
                return False
        return True

    def _parse_string(self, str_str: str, json5_str: str, str_start_idx: int) -> str:
        def replace_escape_sequences_and_continuations(match):
            """Unescape escape sequences and line continuations in a string.
            escape sequences replaced: `\'`, `\"`, `\\`, `\b`, `\f`, `\n`, `\r`, `\t`,
                `\v`, `\0`
            line continuations replaced: `\\` followed by a newline character
            """
            if match.group(1):
                # in strict mode, control characters are not allowed
                if self._strict and match.group(1) in {"t", "n", "r", "0"}:
                    raise JSON5DecodeError(
                        ParseErrors.invalid_control_char(),
                        json5_str,
                        str_start_idx + match.start(),
                    )
                return ESCAPE_SEQUENCE[match.group(1)]
            return ""

        return re.sub(
            r"\\([\'\"\\bfnrtv0])|\\\s*\n",
            replace_escape_sequences_and_continuations,
            str_str,
        )


def loads(
    json5_str: str,
    *,
    object_hook: Callable[[dict[str, JsonValue]], Any] | None = None,
    parse_float: Callable[[str], Any] | None = None,
    parse_int: Callable[[str], Any] | None = None,
    parse_constant: Callable[[str], Any] | None = None,
    strict: bool = True,
    object_pairs_hook: Callable[[tuple[str, JsonValue]], Any] | None = None,
) -> Any:
    """TODO"""
    decoder = Json5Decoder(
        object_hook=object_hook,
        parse_float=parse_float,
        parse_int=parse_int,
        parse_constant=parse_constant,
        strict=strict,
        object_pairs_hook=object_pairs_hook,
    )
    return decoder.decode(json5_str)


def load(
    file: TextIO,
    *,
    object_hook: Callable[[dict[str, JsonValue]], Any] | None = None,
    parse_float: Callable[[str], Any] | None = None,
    parse_int: Callable[[str], Any] | None = None,
    parse_constant: Callable[[str], Any] | None = None,
    strict: bool = True,
    object_pairs_hook: Callable[[tuple[str, JsonValue]], Any] | None = None,
) -> Any:
    """Convert JSON5 file to python data."""
    return loads(
        file.read(),
        object_hook=object_hook,
        parse_float=parse_float,
        parse_int=parse_int,
        parse_constant=parse_constant,
        strict=strict,
        object_pairs_hook=object_pairs_hook,
    )
