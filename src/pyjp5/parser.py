"""Parser for JSON5."""

from typing import Literal

from .core import Token, TokenType, JSON5DecodeError, JsonValue
from .err_msg import ParseErrors
from . import utils

BaseType = {TokenType.STRING, TokenType.NUMBER, TokenType.BOOLEAN, TokenType.NULL}


def parse_number(tok_val: str) -> int | float:
    """Parse a number."""
    if "Infinity" in tok_val:
        return float("-inf" if "-" in tok_val else "inf")
    if "NaN" in tok_val:
        return float("-nan" if "-" in tok_val else "nan")
    if "0x" in tok_val or "0X" in tok_val:
        return int(tok_val, 16)
    if "." in tok_val or "e" in tok_val or "E" in tok_val:
        return float(tok_val)
    return int(tok_val)


ParserDType = Literal["object", "array"]
Stack = list[tuple[ParserDType, JsonValue, str | None]]


def parser(buffer: str, tokens: list[Token]) -> JsonValue:
    """Parse tokens into a python data type."""
    # stack contains (type, data, last_key) tuples
    stack: Stack = []
    root: JsonValue | None = None
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
                raise JSON5DecodeError(ParseErrors.expecting_property_name(), buffer, 0)
            # Insert into dict under the key
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
            raise JSON5DecodeError(ParseErrors.multiple_root(), buffer, 0)
        root = new_root
        root_defined = True

    idx = 0
    while idx < len(tokens):
        tok = tokens[idx]
        tok_value = buffer[tok.value[0] : tok.value[1]]

        if tok.tk_type == TokenType.PUNCTUATOR and tok_value == "{":
            add_value_to_top({})
            # Push onto the stack
            stack.append(("object", {}, None))

        elif tok.tk_type == TokenType.PUNCTUATOR and tok_value == "}":
            if not stack or stack[-1][0] != "object":
                raise JSON5DecodeError(
                    ParseErrors.unexpected_punctuation("}"), buffer, tok.value[0]
                )
            layer = stack.pop()
            if not stack:
                # If stack is now empty, that means this object is the root
                update_root(layer[1])

        elif tok.tk_type == TokenType.PUNCTUATOR and tok_value == "[":
            add_value_to_top([])
            stack.append(("array", [], None))

        elif tok.tk_type == TokenType.PUNCTUATOR and tok_value == "]":
            if not stack or stack[-1][0] != "array":
                raise JSON5DecodeError(
                    ParseErrors.unexpected_punctuation("]"), buffer, tok.value[0]
                )
            if not stack:
                # If stack is now empty, that means this array is the root
                update_root(stack.pop()[1])

        elif tok.tk_type == TokenType.IDENTIFIER:
            if not stack or stack[-1][0] == "array" or stack[-1][2] is not None:
                # identifier can only be used as a key in an object
                raise JSON5DecodeError(ParseErrors.expecting_value(), buffer, 0)
            stack[-1] = (stack[-1][0], stack[-1][1], tok_value)
        elif tok.tk_type == TokenType.STRING:
            if not utils.validate_line_continuation(tok_value):
                raise JSON5DecodeError(
                    ParseErrors.bad_string_continuation(), buffer, tok.value[0]
                )
            parsed_str = utils.unescape_line_continuation(
                utils.unescape_escaped_sequence(tok_value)
            )
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

        elif tok.tk_type == TokenType.NUMBER:
            parsed_number = parse_number(tok_value)
            # These are scalar values
            if not stack:
                # A bare scalar is root-level
                update_root(parsed_number)
            else:
                add_value_to_top(parsed_number)

        elif tok.tk_type == TokenType.BOOLEAN:
            assert tok_value in {"true", "false"}
            parsed_bool = tok_value == "true"
            if not stack:
                update_root(parsed_bool)
            else:
                add_value_to_top(parsed_bool)

        elif tok.tk_type == TokenType.NULL:
            assert tok_value == "null"
            if not stack:
                update_root(None)
            else:
                add_value_to_top(None)

        elif tok.tk_type == TokenType.PUNCTUATOR and tok_value == ":":
            # Just validate that we are in an object and have a last_key
            if not stack:
                raise JSON5DecodeError(
                    ParseErrors.expecting_value(), buffer, tok.value[0]
                )
            top_type, top_data, top_last_key = stack[-1]
            if top_type != "object" or top_last_key is None:
                raise JSON5DecodeError(
                    ParseErrors.unexpected_colon(), buffer, tok.value[0]
                )
            if idx + 1 >= len(tokens):
                raise JSON5DecodeError(
                    ParseErrors.expecting_value(), buffer, tok.value[0]
                )
            if tokens[idx + 1].tk_type == TokenType.PUNCTUATOR and buffer[
                tokens[idx + 1].value[0]
            ] in {"]", "}", ",", ":"}:
                raise JSON5DecodeError(
                    ParseErrors.unexpected_punctuation(
                        buffer[tokens[idx + 1].value[0]]
                    ),
                    buffer,
                    0,
                )

        elif tok.tk_type == TokenType.PUNCTUATOR and tok_value == ",":
            # Typically just means "expect another key-value or value next"
            # Validate that we are inside an object or array, and that we just
            # finished a value
            pass

        else:
            raise ValueError(f"Unexpected token {tok_value}")

        idx += 1

    # If everything is parsed, the stack should be empty (all objects/arrays closed)
    if stack:
        raise JSON5DecodeError(
            ParseErrors.expecting_value(), buffer, tokens[-1].value[0]
        )

    return root
