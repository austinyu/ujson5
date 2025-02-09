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
HEX_DIGITS = set("0 1 2 3 4 5 6 7 8 9 a b c d e f A B C D E F".split())


"""
LEADING_WS: Leading whitespace before the number
SIGN: Sign of the number (+ or -)
INF_I: 'I' in 'Infinity'
INF_IN: 'n' in 'Infinity'
INF_INF: 'f' in 'Infinity'
INF_INFI: 'i' in 'Infinity'
INF_INFIN: 'n' in 'Infinity'
INF_INFINI: 'i' in 'Infinity'
INF_INFINIT: 't' in 'Infinity'
INF_INFINITY: 'y' in 'Infinity' (accepting)
NAN_N: 'N' in 'NaN'
NAN_NA: 'a' in 'NaN'
NAN_NAN: 'N' in 'NaN' (accepting)
INT_ZERO: Integer zero (accepting)
INT_NONZERO: Non-zero integer (accepting)
DOT_NOINT: Dot without integer part
FRACTION: Fractional part of the number (accepting)
EXP_START: Start of the exponent part
EXP_SIGN: Sign of the exponent
EXP_DIGITS: Digits of the exponent (accepting)
TRAILING_WS: Trailing whitespace after the number (accepting)
HEX_START: Start of a hexadecimal number
HEX_DIGITS: Digits of a hexadecimal number (accepting)
"""
NumberStateLiteral = Literal[
    "LEADING_WS",
    "SIGN",
    "INF_INFINITY",  # accepting
    "NAN_NAN",  # accepting
    "INT_ZERO",  # accepting
    "INT_NONZERO",  # accepting
    "DOT_NOINT",
    "FRACTION",  # accepting
    "EXP_START",
    "EXP_SIGN",
    "EXP_DIGITS",  # accepting
    "TRAILING_WS",  # accepting
    "HEX_START",
    "HEX_DIGITS",  # accepting
]
NumberState: dict[NumberStateLiteral, int] = {
    "LEADING_WS": 0,
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

ACCEPTING_STATES = {
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
            if state in ACCEPTING_STATES and state != NumberState["TRAILING_WS"]:
                number_end_idx = idx
            break

        if state == NumberState["LEADING_WS"]:
            if char.isspace():
                state = NumberState["LEADING_WS"]
                idx += 1
            elif char in {"+", "-"}:
                number_start_idx = idx
                state = NumberState["SIGN"]
                idx += 1
            elif char == "I":
                number_start_idx = idx
                # directly check if we have "Infinity"
                if idx + 8 <= len(buffer) and buffer[idx : idx + 8] == "Infinity":
                    idx += 8
                    state = NumberState["INF_INFINITY"]
                    number_end_idx = idx
                else:
                    raise JSON5DecodeError(
                        msg=err_msg.NumberLexerErrors.invalid_constant(
                            "Infinity", buffer[idx : idx + 8]
                        ),
                        doc=buffer,
                        pos=idx,
                    )
            elif char == "N":
                number_start_idx = idx
                # directly check if we have "NaN"
                if idx + 3 <= len(buffer) and buffer[idx : idx + 3] == "NaN":
                    idx += 3
                    state = NumberState["NAN_NAN"]
                else:
                    raise JSON5DecodeError(
                        msg=err_msg.NumberLexerErrors.invalid_constant(
                            "NaN", buffer[idx : idx + 3]
                        ),
                        doc=buffer,
                        pos=idx,
                    )
            elif char == "0":
                idx += 1
                number_start_idx = idx
                state = NumberState["INT_ZERO"]
            elif char in NON_ZERO_DIGITS:
                idx += 1
                number_start_idx = idx
                state = NumberState["INT_NONZERO"]
            elif char == ".":
                idx += 1
                number_start_idx = idx
                state = NumberState["DOT_NOINT"]
            else:
                handle_unexpected_char(buffer, idx, char)
        elif state == NumberState["SIGN"]:
            if char == "I":
                number_start_idx = idx
                if idx + 8 <= len(buffer) and buffer[idx : idx + 8] == "Infinity":
                    idx += 8
                    state = NumberState["INF_INFINITY"]
                    number_end_idx = idx
                    break
                else:
                    raise JSON5DecodeError(
                        msg=err_msg.NumberLexerErrors.invalid_constant(
                            "Infinity", buffer[idx : idx + 8]
                        ),
                        doc=buffer,
                        pos=idx,
                    )
            elif char == "N":
                number_start_idx = idx
                if idx + 3 <= len(buffer) and buffer[idx : idx + 3] == "NaN":
                    idx += 3
                    state = NumberState["NAN_NAN"]
                    break
                else:
                    raise JSON5DecodeError(
                        msg=err_msg.NumberLexerErrors.invalid_constant(
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
            number_start_idx = idx
        elif state == NumberState["INT_ZERO"]:
            if char == "x" or char == "X":
                state = NumberState["HEX_START"]
            elif char == ".":
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
            idx += 1
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
                number_end_idx = idx
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
                number_end_idx = idx
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
                number_end_idx = idx
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
                    msg=err_msg.NumberLexerErrors.space_in_number(),
                    doc=buffer,
                    pos=idx,
                )
            idx += 1

    if state in ACCEPTING_STATES:
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
    elif state == NumberState["SIGN"]:
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
    elif state == NumberState["HEX_START"]:
        raise JSON5DecodeError(
            msg=err_msg.NumberLexerErrors.no_hex_digits(),
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
