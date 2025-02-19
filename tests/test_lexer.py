"""Test lexer module"""

from os.path import join, dirname

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
    (TokenType.PUNCTUATOR, "{"),
    (TokenType.IDENTIFIER, "unquoted"),
    (TokenType.PUNCTUATOR, ":"),
    (TokenType.STRING, "and you can quote me on that"),
    (TokenType.PUNCTUATOR, ","),
    (TokenType.IDENTIFIER, "singleQuotes"),
    (TokenType.PUNCTUATOR, ":"),
    (TokenType.STRING, 'I can use "double quotes" here'),
    (TokenType.PUNCTUATOR, ","),
    (TokenType.IDENTIFIER, "lineBreaks"),
    (TokenType.PUNCTUATOR, ":"),
    (TokenType.STRING, "Look, Mom! \\\nNo \\\\n's!"),
    (TokenType.PUNCTUATOR, ","),
    (TokenType.IDENTIFIER, "hexadecimal"),
    (TokenType.PUNCTUATOR, ":"),
    (TokenType.NUMBER, "0xdecaf"),
    (TokenType.PUNCTUATOR, ","),
    (TokenType.IDENTIFIER, "leadingDecimalPoint"),
    (TokenType.PUNCTUATOR, ":"),
    (TokenType.NUMBER, ".8675309"),
    (TokenType.PUNCTUATOR, ","),
    (TokenType.IDENTIFIER, "andTrailing"),
    (TokenType.PUNCTUATOR, ":"),
    (TokenType.NUMBER, "8675309."),
    (TokenType.PUNCTUATOR, ","),
    (TokenType.IDENTIFIER, "positiveSign"),
    (TokenType.PUNCTUATOR, ":"),
    (TokenType.NUMBER, "+1"),
    (TokenType.PUNCTUATOR, ","),
    (TokenType.IDENTIFIER, "trailingComma"),
    (TokenType.PUNCTUATOR, ":"),
    (TokenType.STRING, "in objects"),
    (TokenType.PUNCTUATOR, ","),
    (TokenType.IDENTIFIER, "andIn"),
    (TokenType.PUNCTUATOR, ":"),
    (TokenType.PUNCTUATOR, "["),
    (TokenType.STRING, "arrays"),
    (TokenType.PUNCTUATOR, ","),
    (TokenType.PUNCTUATOR, "]"),
    (TokenType.PUNCTUATOR, ","),
    (TokenType.STRING, "backwardsCompatible"),
    (TokenType.PUNCTUATOR, ":"),
    (TokenType.STRING, "with JSON"),
    (TokenType.PUNCTUATOR, ","),
    (TokenType.IDENTIFIER, "null_supported"),
    (TokenType.PUNCTUATOR, ":"),
    (TokenType.NULL, "null"),
    (TokenType.PUNCTUATOR, ","),
    (TokenType.IDENTIFIER, "infinities_supported"),
    (TokenType.PUNCTUATOR, ":"),
    (TokenType.NUMBER, "Infinity"),
    (TokenType.PUNCTUATOR, ","),
    (TokenType.IDENTIFIER, "NaN_supported"),
    (TokenType.PUNCTUATOR, ":"),
    (TokenType.NUMBER, "NaN"),
    (TokenType.PUNCTUATOR, ","),
    (TokenType.PUNCTUATOR, "}"),
]


def test_lexer() -> None:
    """Test lexer"""
    results = tokenize(JSON5_TEXT)
    assert len(results) == len(tokens)
    for r, t in zip(results, tokens):
        assert r.tk_type == t[0]
        r_text = JSON5_TEXT[r.value[0] : r.value[1]]
        assert r_text == t[1]


def test_config_file() -> None:
    """Test config file"""
    with open(join(dirname(__file__), "config.json5"), "r", encoding="utf8") as file:
        config_content = file.read()
    results = tokenize(config_content)
    assert results  # Add appropriate assertions based on expected tokens
