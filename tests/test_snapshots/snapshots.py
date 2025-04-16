"""Snapshots for testing."""

from os.path import dirname
from pathlib import Path
from typing import Annotated, Literal, TypedDict

from annotated_types import Ge, Gt
from pydantic import BaseModel

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


class Property(TypedDict):  # pylint: disable=C0115
    # Property of the house
    house: str  # house name
    # Property of the car
    car: str | None  # car name, can be None


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
    prop: Property  # property of the human


COMPOSITE_EXAMPLE: Human = {
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
    "prop": {
        "house": "Alpha's House",
        "car": "Alpha's Car",
    },
}


class CameraSlice(BaseModel):
    """CameraSlice"""

    # name of the current camera, `camera_obj.device_info.name`
    name: str
    # id of the current camera, `camera_obj.device_info.id`
    camera_id: str
    # exposure time in seconds
    exposure_in_s: Annotated[float, Gt(0)]
    # gain without normalization
    gain: float
    # binning value, (horizontal, vertical)
    binning: tuple[Annotated[float, Gt(0)], Annotated[float, Gt(0)]]
    trigger_mode: int
    number_of_frames_per_burst: int
    # bit depth of the captured image (8, 12, 14, 16)
    bit_depth: Annotated[float, Gt(0)]
    # offset without normalization
    offset: Annotated[float, Ge(0)]
    readout_speed: int  # readout speed is not supported by all cameras


PYDANTIC_EXAMPLE = CameraSlice(
    name="Point Camera",
    camera_id="Point Camera ID",
    exposure_in_s=0.1,
    gain=1.0,
    binning=(2, 2),
    trigger_mode=1,
    number_of_frames_per_burst=10,
    bit_depth=16,
    offset=0.0,
    readout_speed=1000,
)

SNAPSHOT_NAMES: dict[str, str] = {
    "composite_example_default": "composite_example_default.json5",
    "composite_example_with_comments": "composite_example_with_comments.json5",
    "composite_example_no_comments": "composite_example_no_comments.json5",
    "composite_example_no_indent": "composite_example_no_indent.json5",
    "composite_example_7_indent": "composite_example_7_indent.json5",
    "composite_example_special_separators": "composite_example_special_separators.json5",
    "composite_example_with_trailing_comma": "composite_example_with_trailing_comma.json5",
    "composite_example_no_trailing_comma": "composite_example_no_trailing_comma.json5",
    "pydantic_example": "pydantic_example.json5",
}
