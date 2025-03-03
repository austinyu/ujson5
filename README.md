# ujson5

[![CI](https://github.com/austinyu/ujson5/actions/workflows/CI.yml/badge.svg?branch=main)](https://github.com/austinyu/ujson5/actions/workflows/CI.yml)
[![codecov](https://codecov.io/gh/austinyu/ujson5/graph/badge.svg?token=YLMVKROAF2)](https://codecov.io/gh/austinyu/ujson5)

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ujson5)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](https://img.shields.io/badge/mypy-checked-blue)](http://mypy-lang.org/)

Documentation for version: v0.1.0

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
- **Robust test suite** - `ujson5` is tested against the [official JSON5 test suite](https://github.com/json5/json5-tests) to ensure compatibility.
- **Speed** - `ujson5` tokenizer and parser implement DFA-based algorithms for fast parsing, which is only slightly slower than the built-in `json` module.
- **Pythonic** - Comments in python are directly encoded into JSON5 comments. Magic!
- **Quality code base** - `ujson5` is linted with `flake8`, formatted with `black`, and type-checked with `mypy`. What's more? 100% test coverage with `pytest` and `codecov`!
- **Friendly Error Messages** - `ujson5` provides detailed error messages to help you debug your JSON5 files, including the exact location of the error.
- **Type hints** - `ujson5` provides type hints for all public functions and classes.

## Installation

```bash
pip install ujson5
```
