"""Snapshots for testing."""

from os.path import dirname
from pathlib import Path
from typing import Literal, TypedDict

SNAPSHOTS_ROOT = Path(dirname(__file__)) / "snapshots"
DEFAULT_INDENT = 2


class Courses(TypedDict, total=False):
    """Courses"""

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


class ProjectConfig(TypedDict):
    """A configuration for a python project."""

    project_name: str
    pkg_license: Literal["MIT", "GPL", "Apache", "BSD", "Proprietary"]
    # build backends are used to build and distribute your project as a package
    build_backend: (
        Literal["Poetry-core", "Setuptools", "Hatchling", "PDM-backend", "Flit-core"]
        | None
    )  # This is a comment
    # dependency managers are used to manage your project's dependencies
    dependency_manager: Literal["poetry", "uv", "pipenv", "hatch"]
    # static code checkers are used to check your code for errors
    static_code_checkers: list[Literal["flake8", "mypy", "pyright", "pylint"]]
    formatter: list[Literal["black", "ruff", "isort"]]
    spell_checker: Literal["cspell", "codespell"] | None  # spell checkers!
    docs: Literal["mkdocs", "sphinx"] | None
    code_editor: Literal["vs_code"] | None  # code editors are used to edit your code
    # pre-commit is used to run checks before committing code
    pre_commit: bool  # a comment can also be in-line
    cloud_code_base: Literal["github"] | None


class Creature(TypedDict):
    """Creature"""

    height: int  # height of the creature
    # weight of the creature
    # weight cannot be too high!
    weight: int


class Human(Creature):
    """Human"""

    # age of the human
    age: int  # human can be very old!
    # name of the human
    name: str
    # human can be very intelligent
    courses: Courses  # hard-working human
    hobbies: list[str]  # hobbies takes a lot of time...
    project: ProjectConfig


ALPHA: Human = {
    "height": 180,
    "weight": 70,
    "age": 30,
    "name": "Alpha",
    "courses": {
        "CS101": 90,
        "ART101": 80,
        "HIS101": 70,
    },
    "hobbies": ["reading", "swimming", "coding"],
    "project": {
        "project_name": "Alpha's Project",
        "pkg_license": "MIT",
        "build_backend": "Poetry-core",
        "dependency_manager": "poetry",
        "static_code_checkers": ["flake8", "mypy"],
        "formatter": ["black", "isort"],
        "spell_checker": "cspell",
        "docs": "mkdocs",
        "code_editor": "vs_code",
        "pre_commit": True,
        "cloud_code_base": "github",
    },
}


SNAPSHOT_NAMES: dict[str, str] = {
    "alpha_default": "alpha_default.json5",
    "alpha_with_comments": "alpha_with_comments.json5",
    "alpha_no_comments": "alpha_no_comments.json5",
    "alpha_no_indent": "alpha_no_indent.json5",
    "alpha_7_indent": "alpha_7_indent.json5",
    "alpha_special_separators": "alpha_special_separators.json5",
    "alpha_with_trailing_comma": "alpha_with_trailing_comma.json5",
    "alpha_no_trailing_comma": "alpha_no_trailing_comma.json5",
}
