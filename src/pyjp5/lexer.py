"""Lexer for JSON5 documents. This module provides functions to tokenize JSON5
documents. The lexer is implemented as a finite state machine (FSM) with states
and transitions. The lexer is used to tokenize JSON5 documents into tokens. The
tokens are used by the parser to build the abstract syntax tree (AST).
"""

from enum import Enum, auto
from typing import Literal, NamedTuple

from .core import JSON5DecodeError
from .err_msg import (
    LexerErrors,
    NumberLexerErrors,
    StringLexerErrors,
    IdentifierLexerErrors,
)
from . import lexer_consts as consts


class TokenType(Enum):
    """Token types for JSON5 documents"""

    IDENTIFIER = auto()
    PUNCTUATOR = auto()
    STRING = auto()
    NUMBER = auto()
    BOOLEAN = auto()
    NULL = auto()


class Token(NamedTuple):
    """Token representation"""

    tk_type: TokenType
    # start and end index of the token in the document
    value: tuple[int, int]


class TokenResult(NamedTuple):
    """Token result"""

    token: Token
    idx: int


NumberStateLiteral = Literal[
    "NUMBER_START",  # Initial state, waiting for a number
    "SIGN",  # Read a + or - sign, waiting for number
    "INFINITY",  # Read 'Infinity' (accepting)
    "NAN",  # Read 'NaN' (accepting)
    "INT_ZERO",  # Read integer zero (accepting)
    "INT_NONZERO",  # Read non-zero integer (accepting)
    "DOT_NOINT",  # Read dot without integer part, waiting for fraction
    "DOT_INT",  # Read dot with integer part (accepting)
    "FRACTION",  # Read fractional part of the number (accepting)
    "EXP_START",  # Start of the exponent part, waiting for sign or digit
    "EXP_SIGN",  # Read sign of the exponent, waiting for digit
    "EXP_DIGITS",  # Read digits of the exponent (accepting)
    "HEX_START",  # Start of a hexadecimal number, waiting for hex digits
    "HEX_DIGITS",  # Read digits of a hexadecimal number (accepting)
]
NumberState: dict[NumberStateLiteral, int] = {
    "NUMBER_START": 0,
    "SIGN": 1,
    "INFINITY": 2,  # accepting
    "NAN": 3,  # accepting
    "INT_ZERO": 4,
    "INT_NONZERO": 5,
    "DOT_NOINT": 6,
    "DOT_INT": 7,  # accepting
    "FRACTION": 8,
    "EXP_START": 9,
    "EXP_SIGN": 10,
    "EXP_DIGITS": 11,  # accepting
    "HEX_START": 12,
    "HEX_DIGITS": 13,  # accepting
}

NUMBER_ACCEPTING_STATES = {
    NumberState["INFINITY"],
    NumberState["NAN"],
    NumberState["INT_ZERO"],
    NumberState["INT_NONZERO"],
    NumberState["FRACTION"],
    NumberState["EXP_DIGITS"],
    NumberState["HEX_DIGITS"],
    NumberState["DOT_INT"],
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

        if char.isspace() or char in {",", "]", "}"}:
            break

        if state in {NumberState["NUMBER_START"], state == NumberState["SIGN"]}:
            if state == NumberState["NUMBER_START"] and char in {"+", "-"}:
                state = NumberState["SIGN"]
                idx += 1
                continue
            if char == "I":
                inf_end = idx + 1
                while inf_end < buffer_len and not buffer[inf_end].isspace():
                    inf_end += 1
                if buffer[idx:inf_end] == "Infinity":
                    idx += 8
                    state = NumberState["INFINITY"]
                    break
                raise JSON5DecodeError(
                    msg=NumberLexerErrors.invalid_constant(
                        "Infinity", buffer[start_idx:inf_end]
                    ),
                    doc=buffer,
                    pos=idx,
                )
            if char == "N":
                nan_end = idx + 1
                while nan_end < buffer_len and not buffer[nan_end].isspace():
                    nan_end += 1
                if buffer[idx:nan_end] == "NaN":
                    idx += 3
                    state = NumberState["NAN"]
                    break
                raise JSON5DecodeError(
                    msg=NumberLexerErrors.invalid_constant(
                        "NaN", buffer[start_idx:nan_end]
                    ),
                    doc=buffer,
                    pos=idx,
                )
            if char == "0":
                idx += 1
                state = NumberState["INT_ZERO"]
            elif char in consts.NON_ZERO_DIGITS:
                idx += 1
                state = NumberState["INT_NONZERO"]
            elif char == ".":
                idx += 1
                state = NumberState["DOT_NOINT"]
            else:
                _handle_unexpected_char(buffer, idx, char)
        elif state == NumberState["INT_ZERO"]:
            if char in consts.HEX_INDICATORS:
                state = NumberState["HEX_START"]
            elif char == ".":
                state = NumberState["DOT_INT"]
            elif char in consts.EXPONENT_INDICATORS:
                state = NumberState["EXP_START"]
            elif char in consts.DIGITS:
                raise JSON5DecodeError(
                    msg=NumberLexerErrors.leading_zero_followed_by_digit(),
                    doc=buffer,
                    pos=idx,
                )
            else:
                _handle_unexpected_char(buffer, idx, char)
            idx += 1
        elif state == NumberState["INT_NONZERO"]:
            if char in consts.DIGITS:
                state = NumberState["INT_NONZERO"]
            elif char == ".":
                state = NumberState["DOT_INT"]
            elif char in consts.EXPONENT_INDICATORS:
                state = NumberState["EXP_START"]
            else:
                _handle_unexpected_char(buffer, idx, char)
            idx += 1
        elif state in {NumberState["DOT_NOINT"], NumberState["DOT_INT"]}:
            if char in consts.DIGITS:
                state = NumberState["FRACTION"]
            else:
                _handle_unexpected_char(buffer, idx, char)
        elif state == NumberState["FRACTION"]:
            if char in consts.DIGITS:
                state = NumberState["FRACTION"]
            elif char in consts.EXPONENT_INDICATORS:
                state = NumberState["EXP_START"]
            else:
                _handle_unexpected_char(buffer, idx, char)
            idx += 1
        elif state == NumberState["EXP_START"]:
            if char in consts.SIGN:
                state = NumberState["EXP_SIGN"]
            elif char in consts.DIGITS:
                state = NumberState["EXP_DIGITS"]
            else:
                _handle_unexpected_char(buffer, idx, char)
            idx += 1
        elif state in {NumberState["EXP_SIGN"], NumberState["EXP_DIGITS"]}:
            if char in consts.DIGITS:
                state = NumberState["EXP_DIGITS"]
            else:
                _handle_unexpected_char(buffer, idx, char)
            idx += 1
        elif state in {NumberState["HEX_START"], NumberState["HEX_DIGITS"]}:
            if char in consts.HEX_DIGITS:
                state = NumberState["HEX_DIGITS"]
            else:
                _handle_unexpected_char(buffer, idx, char)
            idx += 1

    if state in NUMBER_ACCEPTING_STATES:
        return TokenResult(
            Token(
                tk_type=TokenType.NUMBER,
                value=(start_idx, idx),
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
    elif next_char in consts.ESCAPE_SEQUENCE:  # Single character escape sequence
        idx += 2
    elif next_char == "u":  # Unicode escape sequence
        if idx + 5 >= buffer_len:
            raise JSON5DecodeError(
                msg=LexerErrors.unexpected_eof(),
                doc=buffer,
                pos=idx,
            )
        if all(c in consts.HEX_DIGITS for c in buffer[idx + 2 : idx + 6]):
            idx += 6
        else:
            raise JSON5DecodeError(
                msg=StringLexerErrors.unexpected_escape_sequence(
                    f"\\u{buffer[idx + 2 : idx + 6]}"
                ),
                doc=buffer,
                pos=idx,
            )
    elif next_char == "x":  # Hexadecimal escape sequence
        if idx + 3 >= buffer_len:
            raise JSON5DecodeError(
                msg=LexerErrors.unexpected_eof(),
                doc=buffer,
                pos=idx,
            )
        if all(c in consts.HEX_DIGITS for c in buffer[idx + 2 : idx + 4]):
            idx += 4
        else:
            raise JSON5DecodeError(
                msg=StringLexerErrors.unexpected_escape_sequence(
                    f"\\x{buffer[idx + 2 : idx + 4]}"
                ),
                doc=buffer,
                pos=idx,
            )
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
        start_idx += 1
    elif quote == "'":
        state = STRING_STATES["SINGLE_STRING"]
        start_idx += 1
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
                break
            if char == "\\":
                idx = _escape_handler(buffer, idx)
            else:
                idx += 1
        elif state == STRING_STATES["SINGLE_STRING"]:
            if char == "'":
                state = STRING_STATES["END_STRING"]
                break
            if char == "\\":
                idx = _escape_handler(buffer, idx)
            else:
                idx += 1

    if state == STRING_STATES["END_STRING"]:
        return TokenResult(
            Token(
                tk_type=TokenType.STRING,
                value=(start_idx, idx),
            ),
            idx + 1,  # Skip the closing quote
        )
    raise JSON5DecodeError(
        msg=StringLexerErrors.unexpected_end_of_string(),
        doc=buffer,
        pos=idx,
    )


def validate_identifier_start(buffer: str, idx: int) -> int:
    """Validate the start of an identifier.

    Args:
        buffer (str): JSON5 document
        idx (int): current index. Must point to the start of the identifier

    Returns:
        int: updated index

    Raises:
        JSON5DecodeError: if the identifier is invalid
    """
    start_char = buffer[idx]
    if start_char in {"$", "_"} or start_char in consts.UNICODE_LETTERS:
        idx += 1
    elif start_char == "\\":  # unicode escape sequence
        if idx + 5 >= len(buffer):
            raise JSON5DecodeError(
                msg=LexerErrors.unexpected_eof(),
                doc=buffer,
                pos=idx,
            )
        if buffer[idx + 1] == "u" and all(
            c in consts.HEX_DIGITS for c in buffer[idx + 2 : idx + 6]
        ):
            idx += 6
        else:
            raise JSON5DecodeError(
                msg=IdentifierLexerErrors.invalid_start(
                    f"\\{buffer[idx + 1 : idx + 6]}"
                ),
                doc=buffer,
                pos=idx,
            )
    else:
        raise JSON5DecodeError(
            msg=IdentifierLexerErrors.invalid_start(start_char),
            doc=buffer,
            pos=idx,
        )
    return idx


def tokenize_identifier(buffer: str, idx: int) -> TokenResult:
    """Tokenize an identifier and return the token and the updated index.

    Args:
        buffer (str): JSON5 document
        idx (int): current index. Must point to the start of the identifier

    Returns:
        TokenResult: Token and updated index

    Raises:
        JSON5DecodeError: if the identifier is invalid
    """
    start_idx = idx
    buffer_len = len(buffer)
    idx = validate_identifier_start(buffer, idx)

    while idx < buffer_len:
        char = buffer[idx]

        if char.isspace() or char in consts.PUNCTUATORS:
            break
        is_start_char = False
        try:
            idx = validate_identifier_start(buffer, idx)
            is_start_char = True
        except JSON5DecodeError:
            is_start_char = False
        if is_start_char:
            continue
        if (
            char in consts.UNICODE_COMBINING_MARKS
            or char in consts.UNICODE_DIGITS
            or char in consts.UNICODE_CONNECTORS
            or char in {consts.ZWJ, consts.ZWNJ}
        ):
            idx += 1
        else:
            raise JSON5DecodeError(
                msg=IdentifierLexerErrors.invalid_char(char),
                doc=buffer,
                pos=idx,
            )

    return TokenResult(
        Token(
            tk_type=TokenType.IDENTIFIER,
            value=(start_idx, idx),
        ),
        idx,
    )


def validate_comment(buffer: str, idx: int) -> int:
    """Validate a comment.

    Args:
        buffer (str): JSON5 document
        idx (int): current index. Must point to the start of the comment

    Returns:
        int: updated index

    Raises:
        JSON5DecodeError: if the comment is invalid
    """
    assert buffer[idx] == "/"
    if idx + 1 >= len(buffer):
        raise JSON5DecodeError(
            msg=LexerErrors.unexpected_eof(),
            doc=buffer,
            pos=idx,
        )
    if buffer[idx + 1] == "/":  # Single line comment
        while idx < len(buffer) and buffer[idx] != "\n":
            idx += 1
        return idx + 1 if idx < len(buffer) else idx
    # Multi-line comment
    while idx + 1 < len(buffer) and buffer[idx : idx + 2] != "*/":
        idx += 1
    if idx + 1 == len(buffer):
        raise JSON5DecodeError(
            msg=LexerErrors.unexpected_eof(),
            doc=buffer,
            pos=idx,
        )
    return idx + 2


def tokenize(buffer: str) -> list[Token]:
    """Tokenize a JSON5 document.

    Args:
        buffer (str): JSON5 document

    Returns:
        list[Token]: List of tokens
    """
    tokens: list[Token] = []
    idx: int = 0
    while idx < len(buffer):
        char = buffer[idx]
        if char.isspace():
            idx += 1
        elif char in consts.PUNCTUATORS:
            tokens.append(Token(TokenType.PUNCTUATOR, (idx, idx + 1)))
            idx += 1
        elif char in {"'", '"'}:
            result = tokenize_string(buffer, idx)
            tokens.append(result.token)
            idx = result.idx
        elif char == "/":
            idx = validate_comment(buffer, idx)
        elif char.isdigit() or char in {"+", "-", "."}:
            result = tokenize_number(buffer, idx)
            tokens.append(result.token)
            idx = result.idx
        else:
            result = tokenize_identifier(buffer, idx)
            tok_str = buffer[result.token.value[0] : result.token.value[1]]
            if tok_str in {"true", "false"}:
                token = Token(TokenType.BOOLEAN, result.token.value)
            elif tok_str == "null":
                token = Token(TokenType.NULL, result.token.value)
            elif tok_str in {
                "Infinity",
                "NaN",
                "-Infinity",
                "-NaN",
                "+Infinity",
                "+NaN",
            }:
                token = Token(TokenType.NUMBER, result.token.value)
            else:
                token = result.token
            tokens.append(token)
            idx = result.idx
    return tokens
