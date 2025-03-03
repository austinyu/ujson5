"""Error messages for lexer and parser"""

# pylint: disable=C0116

from typing import Any, Literal
from .core import TOKEN_TYPE_MAP


class NumberDecoderErr:
    """Errors related to number lexer"""

    @staticmethod
    def unexpected_char_in_number(char: str) -> str:
        return f"Unexpected character '{char}' in number"

    @staticmethod
    def leading_zero_followed_by_digit() -> str:
        return "Leading '0' cannot be followed by more digits"

    @staticmethod
    def no_number() -> str:
        return "No number found"

    @staticmethod
    def trailing_dot() -> str:
        return "Trailing dot in number"

    @staticmethod
    def trailing_exponent() -> str:
        return "Trailing exponent in number"

    @staticmethod
    def trailing_exponent_sign() -> str:
        return "Trailing sign in exponent"

    @staticmethod
    def no_hex_digits() -> str:
        return "No hexadecimal digits found"

    @staticmethod
    def invalid_constant(expected: str, actual: str) -> str:
        return f"Invalid constant, expected {expected}, got {actual}"


class StringDecoderErr:
    """Errors related to string lexer"""

    @staticmethod
    def string_invalid_start(char: str) -> str:
        return f"Invalid start of string: <{char}>"

    @staticmethod
    def unexpected_end_of_string() -> str:
        return "Unexpected end of string"

    @staticmethod
    def unexpected_escape_sequence(char: str) -> str:
        return f"Unexpected escape sequence: <{char}>"


class IdentifierDecoderErr:
    """Errors related to identifier lexer"""

    @staticmethod
    def invalid_start(char: str) -> str:
        return f"Invalid start of identifier: <{char}>"

    @staticmethod
    def invalid_char(character: str) -> str:
        return f"Invalid character in identifier: <{character}>"


class DecoderErr:
    """General parse errors"""

    @staticmethod
    def unexpected_eof() -> str:
        return "Unexpected end of file"

    @staticmethod
    def empty_json5() -> str:
        return "Empty JSON5 document"

    @staticmethod
    def expecting_value() -> str:
        return "Expecting value"

    @staticmethod
    def unexpected_identifier() -> str:
        return "Unexpected identifier used as value. Hint: Use quotes for a string"

    @staticmethod
    def expecting_property_name(tk_type: int | None = None) -> str:
        base_msg: str = (
            "Expecting property name that can be either an identifier or a string"
        )
        if tk_type is not None:
            return base_msg + f", got {TOKEN_TYPE_MAP[tk_type]}"
        return base_msg

    @staticmethod
    def expecting_property_value(tk_type: int | None = None) -> str:
        return (
            "Expecting property value that can be one of "
            "{string, number, bool, null, list, object}"
            + f", got {TOKEN_TYPE_MAP[tk_type]}"
            if tk_type is not None
            else ""
        )

    @staticmethod
    def unexpected_punctuation(actual: str) -> str:
        return f"Unexpected punctuation: `{actual}`"

    @staticmethod
    def unexpected_colon_in_array() -> str:
        return "Unexpected colon in array"

    @staticmethod
    def missing_key_with_colon() -> str:
        return (
            "Object entry should have a key of type string or "
            "identifier followed by a colon"
        )

    @staticmethod
    def missing_comma(within: Literal["array", "object"]) -> str:
        return "Missing comma between elements in " + within

    @staticmethod
    def missing_colon() -> str:
        return "Missing colon after object key"

    @staticmethod
    def multiple_root() -> str:
        return "Multiple root elements"

    @staticmethod
    def bad_string_continuation() -> str:
        return "Bad string continuation. `\\` must be followed by spaces and a newline"

    @staticmethod
    def invalid_control_char() -> str:
        return "Invalid control character in string"

    @staticmethod
    def invalid_object_hook() -> str:
        return "Object hook must takes in a dictionary"

    @staticmethod
    def invalid_object_pairs_hook() -> str:
        return "Object pairs hook must takes in a list of tuples with two elements"

    @staticmethod
    def reserved_word(word: str) -> str:
        return f"Reserved word cannot be used as identifier: <{word}>"


class EncoderErrors:
    """Encoder errors"""

    @staticmethod
    def circular_reference() -> str:
        return "Circular reference detected"

    @staticmethod
    def float_out_of_range(obj: Any) -> str:
        return f"Out of range float values are not allowed: {repr(obj)}"

    @staticmethod
    def invalid_key_type(key: Any) -> str:
        return (
            f"keys must be str, int, float, bool or None, not {key.__class__.__name__}"
        )

    @staticmethod
    def unable_to_encode(obj: Any) -> str:
        return f"Object of type {obj.__class__.__name__} is not JSON serializable"

    @staticmethod
    def invalid_typed_dict(obj: Any) -> str:
        return f"Object of type {obj.__class__.__name__} is not a TypedDict"
