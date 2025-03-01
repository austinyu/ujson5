"""Core JSON5 classes and exceptions."""

from typing import Literal, NamedTuple

JsonValue = dict | list | int | float | str | None | bool
"""Type hint for JSON5 values."""
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

    def __reduce__(self) -> tuple:  # pragma: no cover
        return self.__class__, (self.msg, self.doc, self.pos)

    def __str__(self) -> str:  # pragma: no cover
        # Get the line where the error occurred
        line_start = self.doc.rfind("\n", 0, self.pos) + 1
        line_end = self.doc.find("\n", self.pos)
        if line_end == -1:
            line_end = len(self.doc)
        error_line = self.doc[line_start:line_end]

        # Create a pointer to the error column
        pointer = " " * (self.colno - 1) + "^"

        # Format the error message
        return (
            f"{self.msg}: line {self.lineno} column {self.colno} (char {self.pos})\n"
            f"{error_line}\n"
            f"{pointer}"
        )


class JSON5EncodeError(ValueError):
    """Subclass of ValueError raised when encoding fails."""


TokenTypesKey = Literal[
    "IDENTIFIER",
    "STRING",
    "NUMBER",
    "BOOLEAN",
    "NULL",
    "PUN_OPEN_BRACE",
    "PUN_CLOSE_BRACE",
    "PUN_OPEN_BRACKET",
    "PUN_CLOSE_BRACKET",
    "PUN_COLON",
    "PUN_COMMA",
]

TOKEN_TYPE: dict[TokenTypesKey, int] = {
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

TOKEN_TYPE_MAP: dict[int, TokenTypesKey] = {v: k for k, v in TOKEN_TYPE.items()}


class Token(NamedTuple):
    """Token representation"""

    tk_type: int
    # start and end index of the token in the document
    value: tuple[int, int]


class TokenResult(NamedTuple):
    """Token result"""

    token: Token
    idx: int
