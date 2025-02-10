"""Lexer for JSON5 documents. This module provides functions to tokenize JSON5
documents. The lexer is implemented as a finite state machine (FSM) with states
and transitions. The lexer is used to tokenize JSON5 documents into tokens. The
tokens are used by the parser to build the abstract syntax tree (AST).
"""

import re
from enum import Enum, auto
from typing import Literal, NamedTuple

from .core import JSON5DecodeError
from .err_msg import LexerErrors, NumberLexerErrors, StringLexerErrors


class TokenType(Enum):
    """Token types for JSON5 documents"""

    JSON5_IDENTIFIER = auto()
    JSON5_PUNCTUATOR = auto()
    JSON5_STRING = auto()
    JSON5_NUMBER = auto()


class Token(NamedTuple):
    """Token representation"""

    tk_type: TokenType
    value: str


class TokenResult(NamedTuple):
    """Token result"""

    token: Token
    idx: int


LINE_TERMINATOR_SEQUENCE = {
    "\u000a",  # <LF>
    "\u000d",  # <CR> [lookahead ∉ <LF> ]
    "\u2028",  # <LS>
    "\u2029",  # <PS>
    "\u000d\u000a",  # <CR> <LF>
}

ESCAPE_SEQUENCE = {
    "'": "\u0027",  # Apostrophe
    '"': "\u0022",  # Quotation mark
    "\\": "\u005c",  # Reverse solidus
    "b": "\u0008",  # Backspace
    "f": "\u000c",  # Form feed
    "n": "\u000a",  # Line feed
    "r": "\u000d",  # Carriage return
    "t": "\u0009",  # Horizontal tab
    "v": "\u000b",  # Vertical tab
    "0": "\u0000",  # Null
}
TOKEN_END_CHARS = {",", "]", "}", "\n"}


def simplify_escapes(string: str) -> str:
    """Simplify escape sequences in a string. This function replaces line
    continuation sequences with a newline character.

    Args:
        string (str): string with escape sequences

    Returns:
        str: string with escape sequences simplified
    """
    string = re.sub(
        r"(?:\u000D\u000A|[\u000A\u000D\u2028\u2029])",
        "\n",
        string,
    )
    return string


NON_ZERO_DIGITS = set(["1", "2", "3", "4", "5", "6", "7", "8", "9"])
DIGITS = set(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"])
EXPONENT_INDICATORS = {"e", "E"}
HEX_INDICATORS = {"x", "X"}
SIGN = {"+", "-"}
HEX_DIGITS = set(
    [
        "0",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
    ]
)

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


def _handle_unexpected_char(buffer: str, idx: int, char: str) -> None:
    """Handle unexpected characters in a number token.

    Args:
        buffer (str): JSON5 document
        idx (int): current index
        char (str): unexpected character

    Raises:
        JSON5DecodeError: if the character is unexpected
    """
    raise JSON5DecodeError(
        msg=NumberLexerErrors.unexpected_char_in_number(char),
        doc=buffer,
        pos=idx,
    )


def tokenize_number(buffer: str, idx: int) -> TokenResult:
    """Transition Table"""
    state: int = NumberState["NUMBER_START"]
    start_idx = idx

    buffer_len = len(buffer)
    while idx < buffer_len:
        char = buffer[idx]

        if char in TOKEN_END_CHARS:
            break

        if state == NumberState["NUMBER_START"]:
            if char in {"+", "-"}:
                state = NumberState["SIGN"]
                idx += 1
            elif char == "I":
                inf_end = idx + 8
                # directly check if we have "Infinity"
                if inf_end > buffer_len:
                    raise JSON5DecodeError(
                        msg=LexerErrors.unexpected_eof(),
                        doc=buffer,
                        pos=idx,
                    )
                if buffer[idx:inf_end] == "Infinity":
                    idx += 8
                    state = NumberState["INF_INFINITY"]
                else:
                    raise JSON5DecodeError(
                        msg=NumberLexerErrors.invalid_constant(
                            "Infinity", buffer[idx:inf_end]
                        ),
                        doc=buffer,
                        pos=idx,
                    )
            elif char == "N":
                # directly check if we have "NaN"
                if idx + 3 > buffer_len:
                    raise JSON5DecodeError(
                        msg=LexerErrors.unexpected_eof(),
                        doc=buffer,
                        pos=idx,
                    )
                if buffer[idx : idx + 3] == "NaN":
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
                _handle_unexpected_char(buffer, idx, char)
        elif state == NumberState["SIGN"]:
            if char == "I":
                inf_end = idx + 8
                if inf_end > buffer_len:
                    raise JSON5DecodeError(
                        msg=LexerErrors.unexpected_eof(),
                        doc=buffer,
                        pos=idx,
                    )
                if buffer[idx:inf_end] == "Infinity":
                    idx += 8
                    state = NumberState["INF_INFINITY"]
                else:
                    raise JSON5DecodeError(
                        msg=NumberLexerErrors.invalid_constant(
                            "Infinity", buffer[idx:inf_end]
                        ),
                        doc=buffer,
                        pos=idx,
                    )
            elif char == "N":
                if idx + 3 > buffer_len:
                    raise JSON5DecodeError(
                        msg=LexerErrors.unexpected_eof(),
                        doc=buffer,
                        pos=idx,
                    )
                if buffer[idx : idx + 3] == "NaN":
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
                _handle_unexpected_char(buffer, idx, char)
        elif state == NumberState["INT_ZERO"]:
            if char in HEX_INDICATORS:
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
                _handle_unexpected_char(buffer, idx, char)
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
                _handle_unexpected_char(buffer, idx, char)
            idx += 1
        elif state == NumberState["DOT_NOINT"]:
            if char in DIGITS:
                state = NumberState["FRACTION"]
            else:
                _handle_unexpected_char(buffer, idx, char)
        elif state == NumberState["FRACTION"]:
            if char in DIGITS:
                state = NumberState["FRACTION"]
            elif char in EXPONENT_INDICATORS:
                state = NumberState["EXP_START"]
            elif char.isspace():
                state = NumberState["TRAILING_WS"]
            else:
                _handle_unexpected_char(buffer, idx, char)
            idx += 1
        elif state == NumberState["EXP_START"]:
            if char in SIGN:
                state = NumberState["EXP_SIGN"]
            elif char in DIGITS:
                state = NumberState["EXP_DIGITS"]
            else:
                _handle_unexpected_char(buffer, idx, char)
            idx += 1
        elif state == NumberState["EXP_SIGN"]:
            if char in DIGITS:
                state = NumberState["EXP_DIGITS"]
            else:
                _handle_unexpected_char(buffer, idx, char)
            idx += 1
        elif state == NumberState["EXP_DIGITS"]:
            if char in DIGITS:
                state = NumberState["EXP_DIGITS"]
            elif char.isspace():
                state = NumberState["TRAILING_WS"]
            else:
                _handle_unexpected_char(buffer, idx, char)
            idx += 1
        elif state == NumberState["HEX_START"]:
            if char in HEX_DIGITS:
                state = NumberState["HEX_DIGITS"]
            else:
                _handle_unexpected_char(buffer, idx, char)
        elif state == NumberState["HEX_DIGITS"]:
            if char in HEX_DIGITS:
                state = NumberState["HEX_DIGITS"]
            elif char.isspace():
                state = NumberState["TRAILING_WS"]
            else:
                _handle_unexpected_char(buffer, idx, char)
            idx += 1
        elif state in [NumberState["INF_INFINITY"], NumberState["NAN_NAN"]]:
            if char.isspace():
                state = NumberState["TRAILING_WS"]
            else:
                _handle_unexpected_char(buffer, idx, char)
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
                tk_type=TokenType.JSON5_NUMBER,
                value=buffer[start_idx:idx].strip(),
            ),
            idx,
        )
    if state == NumberState["NUMBER_START"]:
        raise JSON5DecodeError(
            msg=NumberLexerErrors.no_number(),
            doc=buffer,
            pos=idx,
        )
    if state == NumberState["SIGN"]:
        raise JSON5DecodeError(
            msg=NumberLexerErrors.no_number(),
            doc=buffer,
            pos=idx,
        )
    if state == NumberState["DOT_NOINT"]:
        raise JSON5DecodeError(
            msg=NumberLexerErrors.trailing_dot(),
            doc=buffer,
            pos=idx,
        )
    if state == NumberState["EXP_START"]:
        raise JSON5DecodeError(
            msg=NumberLexerErrors.trailing_exponent(),
            doc=buffer,
            pos=idx,
        )
    if state == NumberState["HEX_START"]:
        raise JSON5DecodeError(
            msg=NumberLexerErrors.no_hex_digits(),
            doc=buffer,
            pos=idx,
        )
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
    buffer_len = len(buffer)
    if idx + 1 == buffer_len:
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
        while idx < buffer_len:
            character = buffer[idx]
            if character == "\n":
                break
            if not character.isspace():
                break
            idx += 1
        if idx == buffer_len:
            raise JSON5DecodeError(
                msg=LexerErrors.unexpected_eof(),
                doc=buffer,
                pos=idx,
            )
        if buffer[idx] == "\n":
            idx += 1
        else:
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
    """Tokenize a string and return the token and the updated index.

    Args:
        buffer (str): JSON5 document
        idx (int): current index. Must point to the opening quote

    Returns:
        TokenResult: Token and updated index

    Raises:
        JSON5DecodeError: if the string is invalid
    """
    state: int = STRING_STATES["STRING_START"]
    start_idx = idx
    quote = buffer[idx]
    buffer_len = len(buffer)

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

    while idx < buffer_len:
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
                tk_type=TokenType.JSON5_STRING,
                value=substring,
            ),
            idx,
        )
    raise JSON5DecodeError(
        msg=StringLexerErrors.unexpected_end_of_string(),
        doc=buffer,
        pos=idx,
    )
