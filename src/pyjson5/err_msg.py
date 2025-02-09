class NumberLexerErrors:
    @staticmethod
    def unexpected_char_in_number(char: str) -> str:
        return f"Unexpected character '{char}' in number"

    @staticmethod
    def space_in_number() -> str:
        return "Unexpected space in number"

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
