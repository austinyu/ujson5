"""Error messages for lexer and parser"""

# pylint: disable=C0116

from typing import Any


class GeneralError:
    """General errors"""

    @staticmethod
    def unexpected_eof() -> str:
        return "Unexpected end of file"

    @staticmethod
    def empty_json5() -> str:
        return "Empty JSON5 document"


class NumberGeneralError:
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


class StringGeneralError:
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


class IdentifierGeneralError:
    """Errors related to identifier lexer"""

    @staticmethod
    def invalid_start(char: str) -> str:
        return f"Invalid start of identifier: <{char}>"

    @staticmethod
    def invalid_char(character: str) -> str:
        return f"Invalid character in identifier: <{character}>"

    @staticmethod
    def reserved_word(word: str) -> str:
        return f"Reserved word cannot be used as identifier: <{word}>"


class ParseErrors:
    """General parse errors"""

    @staticmethod
    def expecting_value() -> str:
        return "Expecting value"

    @staticmethod
    def expecting_property_name() -> str:
        return "Expecting property name followed by ':'"

    @staticmethod
    def unexpected_punctuation(actual: str) -> str:
        return f"Unexpected punctuation: <{actual}>"

    @staticmethod
    def expecting_punctuation(expected: str) -> str:
        return f"Expecting punctuation: <{expected}>"

    @staticmethod
    def unexpected_token_after_colon(token_type: str) -> str:
        return f"Unexpected token: {token_type} after ':'"

    @staticmethod
    def multiple_root() -> str:
        return "Multiple root elements"

    @staticmethod
    def bad_string_continuation() -> str:
        return "Bad string continuation. `\\` must be followed by a newline"

    @staticmethod
    def invalid_control_char() -> str:
        return "Invalid control character in string"


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
