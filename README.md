pyjson5

https://github.com/marketplace/actions/install-poetry-action



- `poetry install --with test`
- Number DFA

```
LEADING_WS:
  on ws             -> LEADING_WS
  on digit0         -> INT_ZERO
  on digit1_9       -> INT_NONZERO
  on dot            -> DOT_NOINT
  on end            -> ERROR (only whitespace, no number)
  on other          -> ERROR

INT_ZERO (accepting):
  on dot            -> DOT_NOINT
  on exp            -> EXP_START
  on ws             -> TRAILING_WS
  on end            -> ACCEPT
  on digit          -> ERROR (leading '0' cannot be followed by more digits)
  on other          -> ERROR

INT_NONZERO (accepting):
  on digit          -> INT_NONZERO
  on dot            -> DOT_NOINT
  on exp            -> EXP_START
  on ws             -> TRAILING_WS
  on end            -> ACCEPT
  on other          -> ERROR

DOT_NOINT (not accepting):
  on digit          -> FRACTION
  on other          -> ERROR

FRACTION (accepting):
  on digit          -> FRACTION
  on exp            -> EXP_START
  on ws             -> TRAILING_WS
  on end            -> ACCEPT
  on other          -> ERROR

EXP_START (not accepting):
  on sign           -> EXP_SIGN
  on digit          -> EXP_DIGITS
  on other          -> ERROR

EXP_SIGN (not accepting):
  on digit          -> EXP_DIGITS
  on other          -> ERROR

EXP_DIGITS (accepting):
  on digit          -> EXP_DIGITS
  on ws             -> TRAILING_WS
  on end            -> ACCEPT
  on other          -> ERROR

TRAILING_WS (accepting):
  on ws             -> TRAILING_WS
  on end            -> ACCEPT
  on other          -> ERROR

```

```
                # whitespace characters defined here
                # #https://www.ecma-international.org/ecma-262/5.1/#sec-7.2
                # ['\u0009', '\u000b', '\u000c', '\u0020', '\u00a0', '\ufeff']
                # char.isspace() is True for all of these characters
```
