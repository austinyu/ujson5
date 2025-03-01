"""Test lexer module"""

from ujson5.lexer import tokenize, TOKEN_TYPE

JSON5_TEXT = """{
  // comments
  unquoted: 'and you can quote me on that',
  singleQuotes: 'I can use "double quotes" here',
  lineBreaks: "Look, Mom! \\
No \\\\n's!",
  hexadecimal: 0xdecaf,
  leadingDecimalPoint: .8675309, andTrailing: 8675309.,
  positiveSign: +1,
  trailingComma: 'in objects', andIn: ['arrays',],
  "backwardsCompatible": "with JSON",
  null_supported: null,
  infinities_supported: Infinity,
  NaN_supported: NaN,
}"""

tokens: list[tuple[int, str]] = [
    (TOKEN_TYPE["PUN_OPEN_BRACE"], "{"),
    (TOKEN_TYPE["IDENTIFIER"], "unquoted"),
    (TOKEN_TYPE["PUN_COLON"], ":"),
    (TOKEN_TYPE["STRING"], "and you can quote me on that"),
    (TOKEN_TYPE["PUN_COMMA"], ","),
    (TOKEN_TYPE["IDENTIFIER"], "singleQuotes"),
    (TOKEN_TYPE["PUN_COLON"], ":"),
    (TOKEN_TYPE["STRING"], 'I can use "double quotes" here'),
    (TOKEN_TYPE["PUN_COMMA"], ","),
    (TOKEN_TYPE["IDENTIFIER"], "lineBreaks"),
    (TOKEN_TYPE["PUN_COLON"], ":"),
    (TOKEN_TYPE["STRING"], "Look, Mom! \\\nNo \\\\n's!"),
    (TOKEN_TYPE["PUN_COMMA"], ","),
    (TOKEN_TYPE["IDENTIFIER"], "hexadecimal"),
    (TOKEN_TYPE["PUN_COLON"], ":"),
    (TOKEN_TYPE["NUMBER"], "0xdecaf"),
    (TOKEN_TYPE["PUN_COMMA"], ","),
    (TOKEN_TYPE["IDENTIFIER"], "leadingDecimalPoint"),
    (TOKEN_TYPE["PUN_COLON"], ":"),
    (TOKEN_TYPE["NUMBER"], ".8675309"),
    (TOKEN_TYPE["PUN_COMMA"], ","),
    (TOKEN_TYPE["IDENTIFIER"], "andTrailing"),
    (TOKEN_TYPE["PUN_COLON"], ":"),
    (TOKEN_TYPE["NUMBER"], "8675309."),
    (TOKEN_TYPE["PUN_COMMA"], ","),
    (TOKEN_TYPE["IDENTIFIER"], "positiveSign"),
    (TOKEN_TYPE["PUN_COLON"], ":"),
    (TOKEN_TYPE["NUMBER"], "+1"),
    (TOKEN_TYPE["PUN_COMMA"], ","),
    (TOKEN_TYPE["IDENTIFIER"], "trailingComma"),
    (TOKEN_TYPE["PUN_COLON"], ":"),
    (TOKEN_TYPE["STRING"], "in objects"),
    (TOKEN_TYPE["PUN_COMMA"], ","),
    (TOKEN_TYPE["IDENTIFIER"], "andIn"),
    (TOKEN_TYPE["PUN_COLON"], ":"),
    (TOKEN_TYPE["PUN_OPEN_BRACKET"], "["),
    (TOKEN_TYPE["STRING"], "arrays"),
    (TOKEN_TYPE["PUN_COMMA"], ","),
    (TOKEN_TYPE["PUN_CLOSE_BRACKET"], "]"),
    (TOKEN_TYPE["PUN_COMMA"], ","),
    (TOKEN_TYPE["STRING"], "backwardsCompatible"),
    (TOKEN_TYPE["PUN_COLON"], ":"),
    (TOKEN_TYPE["STRING"], "with JSON"),
    (TOKEN_TYPE["PUN_COMMA"], ","),
    (TOKEN_TYPE["IDENTIFIER"], "null_supported"),
    (TOKEN_TYPE["PUN_COLON"], ":"),
    (TOKEN_TYPE["NULL"], "null"),
    (TOKEN_TYPE["PUN_COMMA"], ","),
    (TOKEN_TYPE["IDENTIFIER"], "infinities_supported"),
    (TOKEN_TYPE["PUN_COLON"], ":"),
    (TOKEN_TYPE["NUMBER"], "Infinity"),
    (TOKEN_TYPE["PUN_COMMA"], ","),
    (TOKEN_TYPE["IDENTIFIER"], "NaN_supported"),
    (TOKEN_TYPE["PUN_COLON"], ":"),
    (TOKEN_TYPE["NUMBER"], "NaN"),
    (TOKEN_TYPE["PUN_COMMA"], ","),
    (TOKEN_TYPE["PUN_CLOSE_BRACE"], "}"),
]


def test_lexer() -> None:
    """Test lexer"""
    results = tokenize(JSON5_TEXT)
    assert len(results) == len(tokens)
    for r, t in zip(results, tokens):
        assert r.tk_type == t[0]
        r_text = JSON5_TEXT[r.value[0] : r.value[1]]
        assert r_text == t[1]
