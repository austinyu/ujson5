import re
from enum import Enum, auto
from typing import Literal, NamedTuple, TypedDict

from .core import JSON5DecodeError
from .err_msg import LexerErrors, NumberLexerErrors, StringLexerErrors


class TokenType(Enum):
    JSON5_IDENTIFIER = auto()
    JSON5_PUNCTUATOR = auto()
    JSON5_STRING = auto()
    JSON5_NUMBER = auto()


class Token(TypedDict):
    type: TokenType
    value: str


class TokenResult(NamedTuple):
    token: Token
    idx: int


LINE_TERMINATOR_SEQUENCE = {
    "\u000A",  # <LF>
    "\u000D",  # <CR> [lookahead ∉ <LF> ]
    "\u2028",  # <LS>
    "\u2029",  # <PS>
    "\u000D\u000A",  # <CR> <LF>
}

ESCAPE_SEQUENCE = {
    "'": "\u0027",  # Apostrophe
    '"': "\u0022",  # Quotation mark
    "\\": "\u005C",  # Reverse solidus
    "b": "\u0008",  # Backspace
    "f": "\u000C",  # Form feed
    "n": "\u000A",  # Line feed
    "r": "\u000D",  # Carriage return
    "t": "\u0009",  # Horizontal tab
    "v": "\u000B",  # Vertical tab
    "0": "\u0000",  # Null
}
TOKEN_END_CHARS = {",", "]", "}", "\n"}


def simplify_escapes(s: str) -> str:
    """Simplify escape sequences in a string. This function replaces line
    continuation sequences with a newline character.

    Args:
        s (str): string with escape sequences

    Returns:
        str: string with escape sequences simplified
    """
    s = re.sub(
        r"(?:\u000D\u000A|[\u000A\u000D\u2028\u2029])",
        "\n",
        s,
    )
    return s


NON_ZERO_DIGITS = set("1 2 3 4 5 6 7 8 9".split())
DIGITS = set("0 1 2 3 4 5 6 7 8 9".split())
EXPONENT_INDICATORS = {"e", "E"}
SIGN = {"+", "-"}
HEX_DIGITS = set("0 1 2 3 4 5 6 7 8 9 a b c d e f A B C D E F".split())

NumberStateLiteral = Literal[
    "NUMBER_START",  # Initial state, waiting for a number
    "SIGN",  # Read a + or - sign, waiting for number
    "INF_INFINITY",  # Read 'Infinity' (accepting)
    "NAN_NAN",  # Read 'NaN' (accepting)
    "INT_ZERO",  # Read integer zero (accepting)
    "INT_NONZERO",  # Read non-zero integer (accepting)
    "DOT_NOINT",  # Read dot without integer part, waiting for fraction
    "FRACTION",  # Read fractional part of the number (accepting)
    "EXP_START",  # Start of the exponent part, waiting for sign or digit
    "EXP_SIGN",  # Read sign of the exponent, waiting for digit
    "EXP_DIGITS",  # Read digits of the exponent (accepting)
    "TRAILING_WS",  # Read trailing whitespace after the number (accepting)
    "HEX_START",  # Start of a hexadecimal number, waiting for hex digits
    "HEX_DIGITS",  # Read digits of a hexadecimal number (accepting)
]
NumberState: dict[NumberStateLiteral, int] = {
    "NUMBER_START": 0,
    "SIGN": 1,
    "INF_INFINITY": 2,  # accepting
    "NAN_NAN": 3,  # accepting
    "INT_ZERO": 4,
    "INT_NONZERO": 5,
    "DOT_NOINT": 6,
    "FRACTION": 7,
    "EXP_START": 8,
    "EXP_SIGN": 9,
    "EXP_DIGITS": 10,  # accepting
    "TRAILING_WS": 11,  # accepting
    "HEX_START": 12,
    "HEX_DIGITS": 13,  # accepting
}

NUMBER_ACCEPTING_STATES = {
    NumberState["INF_INFINITY"],
    NumberState["NAN_NAN"],
    NumberState["INT_ZERO"],
    NumberState["INT_NONZERO"],
    NumberState["FRACTION"],
    NumberState["EXP_DIGITS"],
    NumberState["HEX_DIGITS"],
    NumberState["TRAILING_WS"],
}


def handle_unexpected_char(buffer: str, idx: int, char: str) -> None:
    raise JSON5DecodeError(
        msg=NumberLexerErrors.unexpected_char_in_number(char),
        doc=buffer,
        pos=idx,
    )


def tokenize_number(buffer: str, idx: int) -> TokenResult:
    """Transition Table"""
    state: int = NumberState["NUMBER_START"]
    start_idx = idx
    while idx < len(buffer):
        char = buffer[idx]

        if char in TOKEN_END_CHARS:
            break

        if state == NumberState["NUMBER_START"]:
            if char in {"+", "-"}:
                state = NumberState["SIGN"]
                idx += 1
            elif char == "I":
                # directly check if we have "Infinity"
                if idx + 8 > len(buffer):
                    raise JSON5DecodeError(
                        msg=LexerErrors.unexpected_eof(),
                        doc=buffer,
                        pos=idx,
                    )
                elif buffer[idx : idx + 8] == "Infinity":
                    idx += 8
                    state = NumberState["INF_INFINITY"]
                else:
                    raise JSON5DecodeError(
                        msg=NumberLexerErrors.invalid_constant(
                            "Infinity", buffer[idx : idx + 8]
                        ),
                        doc=buffer,
                        pos=idx,
                    )
            elif char == "N":
                # directly check if we have "NaN"
                if idx + 3 > len(buffer):
                    raise JSON5DecodeError(
                        msg=LexerErrors.unexpected_eof(),
                        doc=buffer,
                        pos=idx,
                    )
                elif buffer[idx : idx + 3] == "NaN":
                    idx += 3
                    state = NumberState["NAN_NAN"]
                else:
                    raise JSON5DecodeError(
                        msg=NumberLexerErrors.invalid_constant(
                            "NaN", buffer[idx : idx + 3]
                        ),
                        doc=buffer,
                        pos=idx,
                    )
            elif char == "0":
                idx += 1
                state = NumberState["INT_ZERO"]
            elif char in NON_ZERO_DIGITS:
                idx += 1
                state = NumberState["INT_NONZERO"]
            elif char == ".":
                idx += 1
                state = NumberState["DOT_NOINT"]
            else:
                handle_unexpected_char(buffer, idx, char)
        elif state == NumberState["SIGN"]:
            if char == "I":
                if idx + 8 > len(buffer):
                    raise JSON5DecodeError(
                        msg=LexerErrors.unexpected_eof(),
                        doc=buffer,
                        pos=idx,
                    )
                elif buffer[idx : idx + 8] == "Infinity":
                    idx += 8
                    state = NumberState["INF_INFINITY"]
                else:
                    raise JSON5DecodeError(
                        msg=NumberLexerErrors.invalid_constant(
                            "Infinity", buffer[idx : idx + 8]
                        ),
                        doc=buffer,
                        pos=idx,
                    )
            elif char == "N":
                if idx + 3 > len(buffer):
                    raise JSON5DecodeError(
                        msg=LexerErrors.unexpected_eof(),
                        doc=buffer,
                        pos=idx,
                    )
                elif buffer[idx : idx + 3] == "NaN":
                    idx += 3
                    state = NumberState["NAN_NAN"]
                else:
                    raise JSON5DecodeError(
                        msg=NumberLexerErrors.invalid_constant(
                            "NaN", buffer[idx : idx + 3]
                        ),
                        doc=buffer,
                        pos=idx,
                    )
            elif char == "0":
                idx += 1
                state = NumberState["INT_ZERO"]
            elif char in NON_ZERO_DIGITS:
                idx += 1
                state = NumberState["INT_NONZERO"]
            elif char == ".":
                idx += 1
                state = NumberState["DOT_NOINT"]
            else:
                handle_unexpected_char(buffer, idx, char)
        elif state == NumberState["INT_ZERO"]:
            if char == "x" or char == "X":
                state = NumberState["HEX_START"]
            elif char == ".":
                state = NumberState["DOT_NOINT"]
            elif char in EXPONENT_INDICATORS:
                state = NumberState["EXP_START"]
            elif char.isspace():
                state = NumberState["TRAILING_WS"]
            elif char in DIGITS:
                raise JSON5DecodeError(
                    msg=NumberLexerErrors.leading_zero_followed_by_digit(),
                    doc=buffer,
                    pos=idx,
                )
            else:
                handle_unexpected_char(buffer, idx, char)
            idx += 1
        elif state == NumberState["INT_NONZERO"]:
            if char in DIGITS:
                state = NumberState["INT_NONZERO"]
            elif char == ".":
                state = NumberState["DOT_NOINT"]
            elif char in EXPONENT_INDICATORS:
                state = NumberState["EXP_START"]
            elif char.isspace():
                state = NumberState["TRAILING_WS"]
            else:
                handle_unexpected_char(buffer, idx, char)
            idx += 1
        elif state == NumberState["DOT_NOINT"]:
            if char in DIGITS:
                state = NumberState["FRACTION"]
            else:
                handle_unexpected_char(buffer, idx, char)
        elif state == NumberState["FRACTION"]:
            if char in DIGITS:
                state = NumberState["FRACTION"]
            elif char in EXPONENT_INDICATORS:
                state = NumberState["EXP_START"]
            elif char.isspace():
                state = NumberState["TRAILING_WS"]
            else:
                handle_unexpected_char(buffer, idx, char)
            idx += 1
        elif state == NumberState["EXP_START"]:
            if char in SIGN:
                state = NumberState["EXP_SIGN"]
            elif char in DIGITS:
                state = NumberState["EXP_DIGITS"]
            else:
                handle_unexpected_char(buffer, idx, char)
            idx += 1
        elif state == NumberState["EXP_SIGN"]:
            if char in DIGITS:
                state = NumberState["EXP_DIGITS"]
            else:
                handle_unexpected_char(buffer, idx, char)
            idx += 1
        elif state == NumberState["EXP_DIGITS"]:
            if char in DIGITS:
                state = NumberState["EXP_DIGITS"]
            elif char.isspace():
                state = NumberState["TRAILING_WS"]
            else:
                handle_unexpected_char(buffer, idx, char)
            idx += 1
        elif state == NumberState["HEX_START"]:
            if char in HEX_DIGITS:
                state = NumberState["HEX_DIGITS"]
            else:
                handle_unexpected_char(buffer, idx, char)
        elif state == NumberState["HEX_DIGITS"]:
            if char in HEX_DIGITS:
                state = NumberState["HEX_DIGITS"]
            elif char.isspace():
                state = NumberState["TRAILING_WS"]
            else:
                handle_unexpected_char(buffer, idx, char)
            idx += 1
        elif state in [NumberState["INF_INFINITY"], NumberState["NAN_NAN"]]:
            if char.isspace():
                state = NumberState["TRAILING_WS"]
            else:
                handle_unexpected_char(buffer, idx, char)
            idx += 1
        else:
            assert state == NumberState["TRAILING_WS"], state
            if char.isspace():
                state = NumberState["TRAILING_WS"]
            else:
                raise JSON5DecodeError(
                    msg=NumberLexerErrors.space_in_number(),
                    doc=buffer,
                    pos=idx,
                )
            idx += 1

    if state in NUMBER_ACCEPTING_STATES:
        return TokenResult(
            Token(
                type=TokenType.JSON5_NUMBER,
                value=buffer[start_idx:idx].strip(),
            ),
            idx,
        )
    elif state == NumberState["NUMBER_START"]:
        raise JSON5DecodeError(
            msg=NumberLexerErrors.no_number(),
            doc=buffer,
            pos=idx,
        )
    elif state == NumberState["SIGN"]:
        raise JSON5DecodeError(
            msg=NumberLexerErrors.no_number(),
            doc=buffer,
            pos=idx,
        )
    elif state == NumberState["DOT_NOINT"]:
        raise JSON5DecodeError(
            msg=NumberLexerErrors.trailing_dot(),
            doc=buffer,
            pos=idx,
        )
    elif state == NumberState["EXP_START"]:
        raise JSON5DecodeError(
            msg=NumberLexerErrors.trailing_exponent(),
            doc=buffer,
            pos=idx,
        )
    elif state == NumberState["HEX_START"]:
        raise JSON5DecodeError(
            msg=NumberLexerErrors.no_hex_digits(),
            doc=buffer,
            pos=idx,
        )
    else:
        assert state == NumberState["EXP_SIGN"], state
        raise JSON5DecodeError(
            msg=NumberLexerErrors.trailing_exponent_sign(),
            doc=buffer,
            pos=idx,
        )


StringStateLiteral = Literal[
    "STRING_START",  # Initial state, waiting for a string
    "DOUBLE_STRING",
    "SINGLE_STRING",
    "END_STRING",  # accepting
]
STRING_STATES: dict[StringStateLiteral, int] = {
    "STRING_START": 0,
    "DOUBLE_STRING": 1,
    "SINGLE_STRING": 2,
    "END_STRING": 3,  # accepting
}


def _escape_handler(buffer: str, idx: int) -> int:
    """Handle escape sequences

    Args:
        buffer (str): JSON5 document
        idx (int): current index. Must point to the escape character

    Returns:
        int: updated index

    Raises:
        JSON5DecodeError: if the escape sequence is invalid
    """
    assert buffer[idx] == "\\"
    if idx + 1 == len(buffer):
        raise JSON5DecodeError(
            msg=LexerErrors.unexpected_eof(),
            doc=buffer,
            pos=idx,
        )
    next_char = buffer[idx + 1]

    if next_char == "\n":  # Line continuation
        idx += 2
    elif next_char.isspace():  # Ignore whitespace
        idx += 2
        while idx < len(buffer):
            character = buffer[idx]
            if character == "\n":
                break
            elif character.isspace():
                idx += 1
            else:
                break
        if idx == len(buffer):
            raise JSON5DecodeError(
                msg=LexerErrors.unexpected_eof(),
                doc=buffer,
                pos=idx,
            )
        elif buffer[idx] == "\n":
            idx += 1
        else:
            print(buffer[: idx + 1], f"<{buffer[idx]}>")
            raise JSON5DecodeError(
                msg=StringLexerErrors.unexpected_end_of_string(),
                doc=buffer,
                pos=idx,
            )
    elif next_char in ESCAPE_SEQUENCE:  # Single character escape sequence
        idx += 2
    else:
        raise JSON5DecodeError(
            msg=StringLexerErrors.unexpected_escape_sequence(f"\\{next_char}"),
            doc=buffer,
            pos=idx,
        )
    return idx


def tokenize_string(buffer: str, idx: int) -> TokenResult:
    state: int = STRING_STATES["STRING_START"]
    start_idx = idx
    quote = buffer[idx]
    if quote == '"':
        state = STRING_STATES["DOUBLE_STRING"]
    elif quote == "'":
        state = STRING_STATES["SINGLE_STRING"]
    else:
        raise JSON5DecodeError(
            msg=StringLexerErrors.string_invalid_start(quote),
            doc=buffer,
            pos=idx,
        )
    idx += 1

    while idx < len(buffer):
        assert state != STRING_STATES["STRING_START"], state

        char = buffer[idx]

        if char == "\n":
            break

        if state == STRING_STATES["DOUBLE_STRING"]:
            if char == '"':
                state = STRING_STATES["END_STRING"]
                idx += 1
            elif char == "\\":
                idx = _escape_handler(buffer, idx)
            else:
                idx += 1
        elif state == STRING_STATES["SINGLE_STRING"]:
            if char == "'":
                state = STRING_STATES["END_STRING"]
                idx += 1
            elif char == "\\":
                idx = _escape_handler(buffer, idx)
            else:
                idx += 1
        else:
            assert state == STRING_STATES["END_STRING"], state
            if char.isspace():
                idx += 1
            else:
                raise JSON5DecodeError(
                    msg="Unexpected character after string",
                    doc=buffer,
                    pos=idx,
                )

    if state == STRING_STATES["END_STRING"]:
        substring = buffer[start_idx:idx].strip()
        # Unescape escape sequences
        substring = re.sub(
            r"\\([\'\"\\bfnrtv0])",
            lambda match: ESCAPE_SEQUENCE[str(match.group(1))],
            substring,
        )
        # Unescape line continuation
        substring = re.sub(r"\\\s*\n", "\n", substring)
        return TokenResult(
            Token(
                type=TokenType.JSON5_STRING,
                value=substring,
            ),
            idx,
        )
    else:
        raise JSON5DecodeError(
            msg=StringLexerErrors.unexpected_end_of_string(),
            doc=buffer,
            pos=idx,
        )
