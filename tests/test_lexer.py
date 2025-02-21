"""Test lexer module"""

from pyjp5.lexer import tokenize, TokenType


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

tokens: list[tuple[TokenType, str]] = [
    (TokenType.PUN_OPEN_BRACE, "{"),
    (TokenType.IDENTIFIER, "unquoted"),
    (TokenType.PUN_COLON, ":"),
    (TokenType.STRING, "and you can quote me on that"),
    (TokenType.PUN_COMMA, ","),
    (TokenType.IDENTIFIER, "singleQuotes"),
    (TokenType.PUN_COLON, ":"),
    (TokenType.STRING, 'I can use "double quotes" here'),
    (TokenType.PUN_COMMA, ","),
    (TokenType.IDENTIFIER, "lineBreaks"),
    (TokenType.PUN_COLON, ":"),
    (TokenType.STRING, "Look, Mom! \\\nNo \\\\n's!"),
    (TokenType.PUN_COMMA, ","),
    (TokenType.IDENTIFIER, "hexadecimal"),
    (TokenType.PUN_COLON, ":"),
    (TokenType.NUMBER, "0xdecaf"),
    (TokenType.PUN_COMMA, ","),
    (TokenType.IDENTIFIER, "leadingDecimalPoint"),
    (TokenType.PUN_COLON, ":"),
    (TokenType.NUMBER, ".8675309"),
    (TokenType.PUN_COMMA, ","),
    (TokenType.IDENTIFIER, "andTrailing"),
    (TokenType.PUN_COLON, ":"),
    (TokenType.NUMBER, "8675309."),
    (TokenType.PUN_COMMA, ","),
    (TokenType.IDENTIFIER, "positiveSign"),
    (TokenType.PUN_COLON, ":"),
    (TokenType.NUMBER, "+1"),
    (TokenType.PUN_COMMA, ","),
    (TokenType.IDENTIFIER, "trailingComma"),
    (TokenType.PUN_COLON, ":"),
    (TokenType.STRING, "in objects"),
    (TokenType.PUN_COMMA, ","),
    (TokenType.IDENTIFIER, "andIn"),
    (TokenType.PUN_COLON, ":"),
    (TokenType.PUN_OPEN_BRACKET, "["),
    (TokenType.STRING, "arrays"),
    (TokenType.PUN_COMMA, ","),
    (TokenType.PUN_CLOSE_BRACKET, "]"),
    (TokenType.PUN_COMMA, ","),
    (TokenType.STRING, "backwardsCompatible"),
    (TokenType.PUN_COLON, ":"),
    (TokenType.STRING, "with JSON"),
    (TokenType.PUN_COMMA, ","),
    (TokenType.IDENTIFIER, "null_supported"),
    (TokenType.PUN_COLON, ":"),
    (TokenType.NULL, "null"),
    (TokenType.PUN_COMMA, ","),
    (TokenType.IDENTIFIER, "infinities_supported"),
    (TokenType.PUN_COLON, ":"),
    (TokenType.NUMBER, "Infinity"),
    (TokenType.PUN_COMMA, ","),
    (TokenType.IDENTIFIER, "NaN_supported"),
    (TokenType.PUN_COLON, ":"),
    (TokenType.NUMBER, "NaN"),
    (TokenType.PUN_COMMA, ","),
    (TokenType.PUN_CLOSE_BRACE, "}"),
]


def test_lexer() -> None:
    """Test lexer"""
    results = tokenize(JSON5_TEXT)
    assert len(results) == len(tokens)
    for r, t in zip(results, tokens):
        assert r.tk_type == t[0]
        r_text = JSON5_TEXT[r.value[0] : r.value[1]]
        assert r_text == t[1]
