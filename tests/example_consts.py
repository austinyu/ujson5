"""constants related to examples from the official JSON5 test suite."""

from os.path import dirname, join
from os import listdir

EXAMPLE_ROOT = join(dirname(__file__), "json5_examples")

CATEGORIES = [
    "arrays",
    "comments",
    "misc",
    "new-lines",
    "numbers",
    "objects",
    "strings",
    "todo",
]

VALID_EXAMPLES = [
    join(EXAMPLE_ROOT, cat, f)
    for cat in CATEGORIES
    for f in listdir(join(EXAMPLE_ROOT, cat))
    if f.endswith(".json5") or f.endswith(".json")
]

INVALID_EXAMPLES = [
    join(EXAMPLE_ROOT, cat, f)
    for cat in CATEGORIES
    for f in listdir(join(EXAMPLE_ROOT, cat))
    if f.endswith(".js") or f.endswith(".txt")
]
