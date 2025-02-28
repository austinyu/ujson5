# pyjp5

![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)
[![CI](https://github.com/austinyu/pyjp5/actions/workflows/CI.yml/badge.svg?branch=main)](https://github.com/austinyu/pyjp5/actions/workflows/CI.yml)
[![codecov](https://codecov.io/gh/austinyu/pyjp5/graph/badge.svg?token=YLMVKROAF2)](https://codecov.io/gh/austinyu/pyjp5)
[![python](https://img.shields.io/badge/Python-3.10-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![python](https://img.shields.io/badge/Python-3.11-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![python](https://img.shields.io/badge/Python-3.12-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![python](https://img.shields.io/badge/Python-3.13-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

[Website](https://austinyu.github.io/pyjp5/)

## Setup development environment

- Install [poetry](https://python-poetry.org/docs/)
- `poetry install --with dev`
- `pre-commit install`

TODOs

- ruler implementation
- CLI implementation
- comments extraction
- versioning docs using `mike`
- add docstring examples
- add optional arg to encode to cache comments in frozen or optimized mode
- makefile automation

## Comment Extraction Examples

```python

courses = {
    # any comments before the dict entry belong to the entry
    "CS101": 93,
    # you can also add comments with multiple lines just like this one.
    # In this case, the comments in JSON5 will also be multi-line
    "ART101": 87,
    "HIS101": 65,  # a comment can also be in-line
}

# encoded json5
"""
{
    // any comments before the dict entry belong to the entry
    "CS101": 93,
    // you can also add comments with multiple lines just like this one.
    // In this case, the comments in JSON5 will also be multi-line
    "ART101": 87,
    "HIS101": 65,  // a comment can also be in-line
}
"""

class Courses(TypedDict, total=False):
    # you can also add comments in the TypedDict
    CS101: int
    # Multi-line comments are also supported
    # In this case, the comments in JSON5 will also be multi-line
    # The entries of dictionaries that implement this TypedDict will be commented
    ART101: int
    HIS101: int  # a comment can also be in-line
    # if a dictionary does not contain all the keys, only the keys that are
    # present will be commented
    LIT101: int

tom_courses: Courses = {
    "CS101": 93,
    "ART101": 87,
    # comments in dict will override the comments in TypedDict
    "HIS101": 65,  # in this case, HIS101 comments will be overridden
}

judy_courses: Courses = {
    "CS101": 93,
    "ART101": 87,
    "HIS101": 65,
    "LIT101": 78,
}


# encoded json5 for tom_courses
"""
{
    // you can also add comments in the TypedDict
    "CS101": 93,
    // Multi-line comments are also supported
    // In this case, the comments in JSON5 will also be multi-line
    // The entries of dictionaries that implement this TypedDict will be commented
    "ART101": 87,
    // comments in dict will override the comments in TypedDict
    "HIS101": 65,  // in this case, HIS101 comments will be overridden
}
"""

# encoded json5 for judy_courses
"""
{
    // you can also add comments in the TypedDict
    "CS101": 93,
    // Multi-line comments are also supported
    // In this case, the comments in JSON5 will also be multi-line
    // The entries of dictionaries that implement this TypedDict will be commented
    "ART101": 87,
    "HIS101": 65,  // a comment can also be in-line
    // if a dictionary does not contain all the keys, only the keys that are
    // present will be commented
    "LIT101": 78,
}
"""

```

```python
check_list = [
    # list items can also be commented
    "apple",
    # indeed, multiple lines are allowed
    # just like this
    "banana",
    # you can also use a combination of block and inline comments
    "cherry",  # and inline comments are also supported
]

# encoded json5
"""
[
    // list items can also be commented
    "apple",
    // indeed, multiple lines are allowed
    // just like this
    "banana",
    // you can also use a combination of block and inline comments
    "cherry",  // and inline comments are also supported
]
"""
```

## CLIs

- `poetry install --with [group]`
- `poetry add --group [group] [dep]`
- `mkdocs server`
