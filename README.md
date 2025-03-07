# ujson5

[Documentation](https://austinyu.github.io/ujson5/)

## Feature Comparison

|                 |  |
|------------------------|--------|
| CI/CD  | [![CI](https://github.com/austinyu/ujson5/actions/workflows/CI.yml/badge.svg?branch=main)](https://github.com/austinyu/ujson5/actions/workflows/CI.yml) <br> [![build docs](https://github.com/austinyu/ujson5/actions/workflows/docs.yml/badge.svg)](https://github.com/austinyu/ujson5/actions/workflows/docs.yml)   |
| Coverage / Codspeed      | [![codecov](https://codecov.io/gh/austinyu/ujson5/graph/badge.svg?token=YLMVKROAF2)](https://codecov.io/gh/austinyu/ujson5) <br>[![CodSpeed Badge](https://img.shields.io/endpoint?url=https://codspeed.io/badge.json)](https://codspeed.io/austinyu/ujson5)     |
| Package | ![PyPI - Version](https://img.shields.io/pypi/v/ujson5) <br> ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ujson5) <br> ![PyPI - License](https://img.shields.io/pypi/l/ujson5)  <br> ![PyPI - Downloads](https://img.shields.io/pypi/dm/ujson5)     |
| Meta  | [![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit) <br> [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) <br> [![Checked with mypy](https://img.shields.io/badge/mypy-checked-blue)](http://mypy-lang.org/) |


`ujson5` is a Python that encodes and decodes [JSON5](https://json5.org/), a superset of JSON that supports many human-friendly features such as comments, trailing commas, and more!

## Why use JSON5?

Direct quote from the [JSON5 website](https://json5.org/):

JSON5 was started in 2012, and as of 2022, now gets **[>65M downloads/week](https://www.npmjs.com/package/json5)**,
ranks in the **[top 0.1%](https://gist.github.com/anvaka/8e8fa57c7ee1350e3491)** of the most depended-upon packages on npm,
and has been adopted by major projects like
**[Chromium](https://source.chromium.org/chromium/chromium/src/+/main:third_party/blink/renderer/platform/runtime_enabled_features.json5;drc=5de823b36e68fd99009a29281b17bc3a1d6b329c),
[Next.js](https://github.com/vercel/next.js/blob/b88f20c90bf4659b8ad5cb2a27956005eac2c7e8/packages/next/lib/find-config.ts#L43-L46),
[Babel](https://babeljs.io/docs/en/config-files#supported-file-extensions),
[Retool](https://community.retool.com/t/i-am-attempting-to-append-several-text-fields-to-a-google-sheet-but-receiving-a-json5-invalid-character-error/7626),
[WebStorm](https://www.jetbrains.com/help/webstorm/json.html),
and [more](https://github.com/json5/json5/wiki/In-the-Wild)**.
It's also natively supported on **[Apple platforms](https://developer.apple.com/documentation/foundation/jsondecoder/3766916-allowsjson5)**
like **macOS** and **iOS**.

## Why use ujson5?

- **Gentle learning curve** - If you know how to use the `json` module in Python, you already know how to use `ujson5`. `ujson5` API is almost identical to the `json` module with some additional features.
- **Robust test suite** - `ujson5` is tested against the most famous JSON5 test suite to ensure compatibility. See the testing section for more information.
- **Speed** - `ujson5` tokenizer and parser implement DFA-based algorithms for fast parsing, which is only slightly slower than the built-in `json` module.
- **Pythonic** - Comments in python are directly encoded into JSON5 comments. Magic!
- **Quality code base** - `ujson5` is linted with `flake8`, formatted with `black`, and type-checked with `mypy`. What's more? 100% test coverage with `pytest` and `codecov`!
- **Friendly Error Messages** - `ujson5` provides detailed error messages to help you debug your JSON5 files, including the exact location of the error.
- **Type hints** - `ujson5` provides type hints for all public functions and classes.

## Installation

```bash
pip install ujson5
```


## Quick Start

You can use `ujson5` just like the built-in `json` module. Here is a quick example:

```python
from typing import TypedDict
import ujson5

# Decode JSON5
json5_str = """
{
  // comments
  key: 'value', // trailing comma
}
"""

data = ujson5.loads(json5_str)
print(data)  # {'key': 'value'}


# Encode JSON5
class Data(TypedDict):
    # multiple long comments
    # are supported
    key: str  # inline comment


data = {"key": "value"}
json5_str = ujson5.dumps(data, Data, indent=2)
print(json5_str)
# {
#   // multiple long comments
#   // are supported
#   "key": "value",  // inline comment
# }

```

## CLI Usage

After installing `ujson5`, you can use the `ujson5` command-line interface to convert JSON5 files to JSON files or simply validate JSON5 files. The CLI interface is the same as the [official JSON5 CLI](https://json5.org/).

### Installation

Make sure you have installed the package in these three ways to use the CLI:

- Install using pipx (recommended): `pipx install ujson5`
- Install to the global interpreter: `pip install ujson5`
- Install to a virtual env and activate it.

### Usage

`ujson5` module can be used as a console script. The basic usage is:

```bash
ujson5 <infile> <outfile> [options]
```

If the optional `infile` and `outfile` arguments are not specified, `sys.stdin` and `sys.stdout` will be used respectively:

```bash
echo '{"json": "obj"}' | ujson5
{
    "json": "obj"
}
```

Options:

- `infile`: The JSON5 file to be validated or converted to JSON. If not specified, read from `sys.stdin`.
- `outfile`: The JSON file to output the converted JSON. If not specified, output to `sys.stdout`.
- `-v`, `--version`: Print the version number.
- `-i`, `--info`: Print the version number and system information.
- `--sort-keys`: Sort the output of dictionaries alphabetically by key.
- `--no-ensure-ascii`: Disable escaping of non-ascii characters, see [ujson5.dumps()][ujson5.dumps] for more information.
- `--indent`, `--no-indent`, `--compact`: Mutually exclusive options for whitespace control.

- `-h`, `--help`: Output usage information

## Testing

`ujson5` is tested against fixtures in the [JSONTestSuite](https://github.com/nst/JSONTestSuite), [nativejson-benchmark](https://github.com/miloyip/nativejson-benchmark), and [json5-tests](https://github.com/json5/json5-tests) repositories. It is tested to not crash against the [Big List of Naughty Strings](https://github.com/minimaxir/big-list-of-naughty-strings).
