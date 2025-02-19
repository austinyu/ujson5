"""Parser for JSON5."""

from typing import Literal

from .core import Token, TokenType, JSON5DecodeError
from .err_msg import ParseErrors
from . import utils

BaseType = {TokenType.STRING, TokenType.NUMBER, TokenType.BOOLEAN, TokenType.NULL}


def parse_string(buffer: str, token: Token) -> str:
    """Parse a string."""
    tok_val = buffer[token.value[0] : token.value[1]]
    return utils.unescape_line_continuation(utils.unescape_escaped_sequence(tok_val))


def parse_number(buffer: str, token: Token) -> int | float:
    """Parse a number."""
    tok_val = buffer[token.value[0] : token.value[1]]
    if tok_val in {"Infinity", "+Infinity"}:
        return float("inf")
    if tok_val == "-Infinity":
        return float("-inf")
    if tok_val == "NaN":
        return float("nan")
    if "." in tok_val or "e" in tok_val or "E" in tok_val:
        return float(tok_val)
    return int(tok_val)


def parse_boolean(buffer: str, token: Token) -> bool:
    """Parse a boolean."""
    tok_val = buffer[token.value[0] : token.value[1]]
    return tok_val == "true"


ParserDType = Literal["dict", "list", "base"]


def parser_rec(
    buffer: str,
    tokens: list[Token],  # dtype: ParserDType = "base"
) -> dict | list | int | float | str | None:
    """Parse tokens into a python data type."""
    if len(tokens) == 0:
        raise JSON5DecodeError(ParseErrors.expecting_value(), buffer, 0)
    if len(tokens) == 1:
        token = tokens[0]
        if token.tk_type == TokenType.STRING:
            return parse_string(buffer, token)
        if token.tk_type == TokenType.NUMBER:
            return parse_number(buffer, token)
        if token.tk_type == TokenType.BOOLEAN:
            return parse_boolean(buffer, token)
        if token.tk_type == TokenType.NULL:
            return None
        raise JSON5DecodeError(ParseErrors.expecting_value(), buffer, 0)
    return None
