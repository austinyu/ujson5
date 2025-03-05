"""This module contains constants used by the lexer."""

import unicodedata

PUNCTUATORS = {
    "{",
    "}",
    "[",
    "]",
    ":",
    ",",
}


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
    # https://262.ecma-international.org/5.1/#sec-7.8.4
    # even though Solidus is not included in the JSON spec
    # it is valid in multiple JSON test suits I found... so I'm including it here
    # Examples:
    #   https://github.com/nst/JSONTestSuite
    #   https://github.com/miloyip/nativejson-benchmark
    "/": "\u002f",  # Solidus
}


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

# defined at https://262.ecma-international.org/5.1/#sec-7.6.1.1
KEYWORDS = {
    "break",
    "do",
    "instanceof",
    "typeof",
    "case",
    "else",
    "new",
    "var",
    "catch",
    "finally",
    "return",
    "void",
    "continue",
    "for",
    "switch",
    "while",
    "debugger",
    "function",
    "this",
    "with",
    "default",
    "if",
    "throw",
    "delete",
    "in",
    "try",
}

FUTURE_RESERVED_WORDS = {
    "class",
    "enum",
    "extends",
    "super",
    "const",
    "export",
    "import",
    "implements",
    "let",
    "private",
    "public",
    "yield",
    "interface",
    "package",
    "protected",
    "static",
}

RESERVED_WORDS = KEYWORDS.union(FUTURE_RESERVED_WORDS).union(
    {
        "null",
        "true",
        "false",
    }
)


# defined at https://262.ecma-international.org/5.1/#sec-7.6
UNICODE_LETTERS = {
    chr(i)
    for i in range(0x110000)
    if unicodedata.category(chr(i)) in {"Lu", "Ll", "Lt", "Lm", "Lo", "Nl"}
}

UNICODE_COMBINING_MARKS = {
    chr(i) for i in range(0x110000) if unicodedata.category(chr(i)) in {"Mn", "Mc"}
}

UNICODE_DIGITS = {
    chr(i) for i in range(0x110000) if unicodedata.category(chr(i)) == "Nd"
}

UNICODE_CONNECTORS = {
    chr(i)
    for i in range(0x110000)
    if (unicodedata.category(chr(i)) == "Pc" and chr(i) != "_")
}

ZWNJ = "\u200c"  # Zero Width Non-Joiner
ZWJ = "\u200d"  # Zero Width Joiner
