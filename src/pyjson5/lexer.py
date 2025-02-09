from enum import Enum, auto
from typing import Literal, NamedTuple, TypedDict

from . import err_msg
from .core import JSON5DecodeError


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


NON_ZERO_DIGITS = set("1 2 3 4 5 6 7 8 9".split())
DIGITS = set("0 1 2 3 4 5 6 7 8 9".split())
EXPONENT_INDICATORS = {"e", "E"}
SIGN = {"+", "-"}


"""
LEADING_WS
    Handles all the whitespace before the numeric literal starts.
INT_ZERO (accepting)
    We have read exactly '0' as the integer part (no more integer digits allowed).
INT_NONZERO (accepting)
    We have read a nonzero digit (possibly more digits) for the integer part.
DOT_NOINT
    We have read '.' but no fraction digits yet.
FRACTION (accepting)
    We are reading fraction digits after '.'.
EXP_START
    We have just read e or E.
EXP_SIGN
    We have read e/E plus a sign (+ or -), but no exponent digits yet.
EXP_DIGITS (accepting)
    We are reading digits in the exponent (at least one digit has been read).
TRAILING_WS (accepting)
    We have finished the numeric literal and are consuming trailing whitespace.
"""
NumberStateLiteral = Literal[
    "LEADING_WS",
    "INT_ZERO",  # accepting
    "INT_NONZERO",  # accepting
    "DOT_NOINT",
    "FRACTION",  # accepting
    "EXP_START",
    "EXP_SIGN",
    "EXP_DIGITS",  # accepting
    "TRAILING_WS",  # accepting
]
NumberState: dict[NumberStateLiteral, int] = {
    "LEADING_WS": 0,
    "INT_ZERO": 1,
    "INT_NONZERO": 2,
    "DOT_NOINT": 3,
    "FRACTION": 4,
    "EXP_START": 5,
    "EXP_SIGN": 6,
    "EXP_DIGITS": 7,
    "TRAILING_WS": 8,
}


def handle_unexpected_char(buffer: str, idx: int, char: str) -> None:
    raise JSON5DecodeError(
        msg=err_msg.NumberLexerErrors.unexpected_char_in_number(char),
        doc=buffer,
        pos=idx,
    )


def tokenize_number(buffer: str, idx: int) -> TokenResult:
    """Transition Table"""
    state: int = NumberState["LEADING_WS"]
    number_start_idx, number_end_idx = idx, idx

    while idx < len(buffer):
        char = buffer[idx]

        if char == ",":
            if state in {
                NumberState["INT_ZERO"],
                NumberState["INT_NONZERO"],
                NumberState["FRACTION"],
                NumberState["EXP_DIGITS"],
            }:
                number_end_idx = idx
            break

        if state == NumberState["LEADING_WS"]:
            if char.isspace():
                state = NumberState["LEADING_WS"]
            elif char == "0":
                number_start_idx = idx
                state = NumberState["INT_ZERO"]
            elif char in NON_ZERO_DIGITS:
                number_start_idx = idx
                state = NumberState["INT_NONZERO"]
            elif char == ".":
                number_start_idx = idx
                state = NumberState["DOT_NOINT"]
            else:
                handle_unexpected_char(buffer, idx, char)
        elif state == NumberState["INT_ZERO"]:
            if char == ".":
                state = NumberState["DOT_NOINT"]
            elif char in EXPONENT_INDICATORS:
                state = NumberState["EXP_START"]
            elif char.isspace():
                number_end_idx = idx
                state = NumberState["TRAILING_WS"]
            elif char in DIGITS:
                raise JSON5DecodeError(
                    msg=err_msg.NumberLexerErrors.leading_zero_followed_by_digit(),
                    doc=buffer,
                    pos=idx,
                )
            else:
                handle_unexpected_char(buffer, idx, char)
        elif state == NumberState["INT_NONZERO"]:
            if char in DIGITS:
                state = NumberState["INT_NONZERO"]
            elif char == ".":
                state = NumberState["DOT_NOINT"]
            elif char in EXPONENT_INDICATORS:
                state = NumberState["EXP_START"]
            elif char.isspace():
                number_end_idx = idx
                state = NumberState["TRAILING_WS"]
            else:
                handle_unexpected_char(buffer, idx, char)
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
                number_end_idx = idx
                state = NumberState["TRAILING_WS"]
            else:
                handle_unexpected_char(buffer, idx, char)
        elif state == NumberState["EXP_START"]:
            if char in SIGN:
                state = NumberState["EXP_SIGN"]
            elif char in DIGITS:
                state = NumberState["EXP_DIGITS"]
            else:
                handle_unexpected_char(buffer, idx, char)
        elif state == NumberState["EXP_SIGN"]:
            if char in DIGITS:
                state = NumberState["EXP_DIGITS"]
            else:
                handle_unexpected_char(buffer, idx, char)
        elif state == NumberState["EXP_DIGITS"]:
            if char in DIGITS:
                state = NumberState["EXP_DIGITS"]
            elif char.isspace():
                number_end_idx = idx
                state = NumberState["TRAILING_WS"]
            else:
                handle_unexpected_char(buffer, idx, char)
        elif state == NumberState["TRAILING_WS"]:
            if char.isspace():
                state = NumberState["TRAILING_WS"]
            else:
                raise JSON5DecodeError(
                    msg=err_msg.NumberLexerErrors.space_in_number(),
                    doc=buffer,
                    pos=idx,
                )
        idx += 1

    if state in {
        NumberState["INT_ZERO"],
        NumberState["INT_NONZERO"],
        NumberState["FRACTION"],
        NumberState["EXP_DIGITS"],
        NumberState["TRAILING_WS"],
    }:
        return TokenResult(
            Token(
                type=TokenType.JSON5_NUMBER,
                value=buffer[number_start_idx:number_end_idx],
            ),
            idx,
        )
    elif state == NumberState["LEADING_WS"]:
        raise JSON5DecodeError(
            msg=err_msg.NumberLexerErrors.no_number(),
            doc=buffer,
            pos=idx,
        )
    elif state == NumberState["DOT_NOINT"]:
        raise JSON5DecodeError(
            msg=err_msg.NumberLexerErrors.trailing_dot(),
            doc=buffer,
            pos=idx,
        )
    elif state == NumberState["EXP_START"]:
        raise JSON5DecodeError(
            msg=err_msg.NumberLexerErrors.trailing_exponent(),
            doc=buffer,
            pos=idx,
        )
    else:
        assert state == NumberState["EXP_SIGN"], state
        raise JSON5DecodeError(
            msg=err_msg.NumberLexerErrors.trailing_exponent_sign(),
            doc=buffer,
            pos=idx,
        )
