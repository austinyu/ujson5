"""Error messages for lexer and parser"""

# pylint: disable=C0116


class LexerErrors:
    """General lexer errors"""

    @staticmethod
    def unexpected_eof() -> str:
        return "Unexpected end of file"


class NumberLexerErrors:
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


class StringLexerErrors:
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


class IdentifierLexerErrors:
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
