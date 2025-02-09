pyjson5

https://github.com/marketplace/actions/install-poetry-action

- `poetry install --with test`


## Formal JSON5Number DFA

• Q (States): { LEADING_WS, SIGN, CHECK_INFINITY, CHECK_NAN, INT_ZERO, INT_NONZERO, DOT_NOINT, FRACTION, EXP_START, EXP_SIGN, EXP_DIGITS, HEX_START, HEX_DIGITS, TRAILING_WS }
• Σ (Alphabet): { digits (0-9), hex digits (0-9A-Fa-f), '.', 'x', 'X', 'e', 'E', '+', '-', 'I', 'N', whitespace, end }
• q₀ (Start State): LEADING_WS
• F (Accepting States): { CHECK_INFINITY, CHECK_NAN, INT_ZERO, INT_NONZERO, FRACTION, EXP_DIGITS, HEX_DIGITS, TRAILING_WS }

Δ (Transition Function) sketch:
• LEADING_WS:
  - on '+'/'-' → SIGN
  - on 'I' → CHECK_INFINITY
  - on 'N' → CHECK_NAN
  - on '0' → INT_ZERO
  - on [1-9] → INT_NONZERO
  - on '.' → DOT_NOINT
  - on ws → LEADING_WS
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

```
                # whitespace characters defined here
                # #https://www.ecma-international.org/ecma-262/5.1/#sec-7.2
                # ['\u0009', '\u000b', '\u000c', '\u0020', '\u00a0', '\ufeff']
                # char.isspace() is True for all of these characters
```
