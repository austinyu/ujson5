# String

## Definition

```
JSON5String::
    "JSON5DoubleStringCharacters _opt"
    'JSON5SingleStringCharacters _opt'
JSON5DoubleStringCharacters::
    JSON5DoubleStringCharacter JSON5DoubleStringCharacters _opt
JSON5SingleStringCharacters::
    JSON5SingleStringCharacter JSON5SingleStringCharacters _opt
JSON5DoubleStringCharacter::
    SourceCharacter but not one of " or \ or LineTerminator
    \EscapeSequence
    LineContinuation
    U+2028
    U+2029
JSON5SingleStringCharacter::
    SourceCharacterbut not one of ' or \ or LineTerminator
    \EscapeSequence
    LineContinuation
    U+2028
    U+2029

LineContinuation ::
    \ LineTerminatorSequence

LineTerminatorSequence ::
    <LF>
    <CR> [lookahead ∉ <LF> ]
    <LS>
    <PS>
    <CR> <LF>
```

| Escape Sequence | Description       | Code Point |
|-----------------|-------------------|------------|
| \'              | Apostrophe        | U+0027     |
| \"              | Quotation mark    | U+0022     |
| \\              | Reverse solidus   | U+005C     |
| \b              | Backspace         | U+0008     |
| \f              | Form feed         | U+000C     |
| \n              | Line feed         | U+000A     |
| \r              | Carriage return   | U+000D     |
| \t              | Horizontal tab    | U+0009     |
| \v              | Vertical tab      | U+000B     |
| \0              | Null              | U+0000     |

## DFA for JSON5 Strings

• Q (States): { STRING_START, DOUBLE_STRING_BODY, SINGLE_STRING_BODY, ESCAPE, LINE_CONTINUATION, END_STRING }
• Σ (Alphabet): { " (double quote), ' (single quote), \ (backslash), any other valid SourceCharacter, end }
• q₀ (Start State): STRING_START
• F (Accepting States): { END_STRING }

Δ (Transition Function) sketch:
• STRING_START:

- on '"' → DOUBLE_STRING_BODY
- on ''' → SINGLE_STRING_BODY
- on other → ERROR
  • DOUBLE_STRING_BODY:
- on backslash → ESCAPE
- on '"' → END_STRING
- on other valid char → DOUBLE_STRING_BODY
  • SINGLE_STRING_BODY:
- on backslash → ESCAPE
- on ''' → END_STRING
- on other valid char → SINGLE_STRING_BODY
  • ESCAPE:
- on valid escape char → (DOUBLE_STRING_BODY or SINGLE_STRING_BODY based on previous state)
- on LineTerminatorSequence → LINE_CONTINUATION
- on other → ERROR
  • LINE_CONTINUATION:
- on valid char → (DOUBLE_STRING_BODY or SINGLE_STRING_BODY based on previous state)
- on other → ERROR
  • END_STRING:
- on end → ACCEPT
- on other → ERROR

# Number

## Definition

```
JSON5Number::
    JSON5NumericLiteral
    +JSON5NumericLiteral
    -JSON5NumericLiteral
JSON5NumericLiteral::
    NumericLiteral
    Infinity
    NaN
NumericLiteral ::
    DecimalLiteral
    HexIntegerLiteral
DecimalLiteral ::
    DecimalIntegerLiteral . DecimalDigits _opt ExponentPart _opt
    . DecimalDigits ExponentPart _opt
    DecimalIntegerLiteral ExponentPart _opt
DecimalIntegerLiteral ::
    0
    NonZeroDigit DecimalDigits _opt
DecimalDigits ::
    DecimalDigit
    DecimalDigits DecimalDigit
DecimalDigit :: one of
    0 1 2 3 4 5 6 7 8 9
NonZeroDigit :: one of
    1 2 3 4 5 6 7 8 9
ExponentPart ::
    ExponentIndicator SignedInteger
ExponentIndicator :: one of
    e E
SignedInteger ::
    DecimalDigits
    + DecimalDigits
    - DecimalDigits
HexIntegerLiteral ::
    0x HexDigit
    0X HexDigit
    HexIntegerLiteral HexDigit
HexDigit :: one of
    0 1 2 3 4 5 6 7 8 9 a b c d e f A B C D E F
```

## DFA

• Q (States): { NUMBER_START, SIGN, CHECK_INFINITY, CHECK_NAN, INT_ZERO, INT_NONZERO, DOT_NOINT, FRACTION, EXP_START, EXP_SIGN, EXP_DIGITS, HEX_START, HEX_DIGITS, TRAILING_WS }
• Σ (Alphabet): { digits (0-9), hex digits (0-9A-Fa-f), '.', 'x', 'X', 'e', 'E', '+', '-', 'I', 'N', whitespace, end }
• q₀ (Start State): NUMBER_START
• F (Accepting States): { CHECK_INFINITY, CHECK_NAN, INT_ZERO, INT_NONZERO, FRACTION, EXP_DIGITS, HEX_DIGITS, TRAILING_WS }

Δ (Transition Function) sketch:
• NUMBER_START:

- on '+'/'-' → SIGN
- on 'I' → CHECK_INFINITY
- on 'N' → CHECK_NAN
- on '0' → INT_ZERO
- on [1-9] → INT_NONZERO
- on '.' → DOT_NOINT
- on end → ERROR
  • SIGN:
- on 'I' → CHECK_INFINITY
- on 'N' → CHECK_NAN
- on '0' → INT_ZERO
- on [1-9] → INT_NONZERO
- on '.' → DOT_NOINT
- on other → ERROR
  • CHECK_INFINITY: Accept if next chars match "Infinity", else ERROR → TRAILING_WS
  • CHECK_NAN: Accept if next chars match "NaN", else ERROR → TRAILING_WS
  • INT_ZERO:
- on 'x'/'X' → HEX_START
- on '.' → DOT_NOINT
- on e/E → EXP_START
- on ws → TRAILING_WS
- on end → ACCEPT
- on digits → ERROR
- on other → ERROR
  • INT_NONZERO:
- on digit → INT_NONZERO
- on '.' → DOT_NOINT
- on e/E → EXP_START
- on ws → TRAILING_WS
- on end → ACCEPT
- on other → ERROR
  • DOT_NOINT:
- on digit → FRACTION
- on other → ERROR
  • FRACTION:
- on digit → FRACTION
- on e/E → EXP_START
- on ws → TRAILING_WS
- on end → ACCEPT
- on other → ERROR
  • EXP_START:
- on '+'/'-' → EXP_SIGN
- on digit → EXP_DIGITS
- on other → ERROR
  • EXP_SIGN:
- on digit → EXP_DIGITS
- on other → ERROR
  • EXP_DIGITS:
- on digit → EXP_DIGITS
- on ws → TRAILING_WS
- on end → ACCEPT
- on other → ERROR
  • HEX_START:
- on hex_digit → HEX_DIGITS
- on other → ERROR
  • HEX_DIGITS:
- on hex_digit → HEX_DIGITS
- on ws → TRAILING_WS
- on end → ACCEPT
- on other → ERROR
  • TRAILING_WS:
- on ws → TRAILING_WS
- on end → ACCEPT
- on other → ERROR
