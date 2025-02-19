"""Core JSON5 classes and exceptions."""

from enum import Enum, auto
from typing import NamedTuple


class JSON5DecodeError(ValueError):
    """Subclass of ValueError with the following additional properties:

    msg: The unformatted error message
    doc: The JSON document being parsed
    pos: The start index of doc where parsing failed
    lineno: The line corresponding to pos
    colno: The column corresponding to pos

    """

    # Note that this exception is used from _json
    def __init__(self, msg: str, doc: str, pos: int) -> None:
        lineno = doc.count("\n", 0, pos) + 1
        colno = pos - doc.rfind("\n", 0, pos)
        err_msg = f"{msg}: line {lineno} column {colno} (char {pos})"
        ValueError.__init__(self, err_msg)
        self.msg = msg
        self.doc = doc
        self.pos = pos
        self.lineno = lineno
        self.colno = colno

    def __reduce__(self) -> tuple:
        return self.__class__, (self.msg, self.doc, self.pos)


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
