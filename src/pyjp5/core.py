"""Core JSON5 classes and exceptions."""

from typing import NamedTuple

JsonValue = dict | list | int | float | str | None | bool
JsonValuePairs = list[tuple[str, JsonValue]]


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


TOKEN_TYPE = {
    "IDENTIFIER": 0,
    "STRING": 1,
    "NUMBER": 2,
    "BOOLEAN": 3,
    "NULL": 4,
    "PUN_OPEN_BRACE": 5,
    "PUN_CLOSE_BRACE": 6,
    "PUN_OPEN_BRACKET": 7,
    "PUN_CLOSE_BRACKET": 8,
    "PUN_COLON": 9,
    "PUN_COMMA": 10,
}


class Token(NamedTuple):
    """Token representation"""

    tk_type: int
    # start and end index of the token in the document
    value: tuple[int, int]


class TokenResult(NamedTuple):
    """Token result"""

    token: Token
    idx: int
