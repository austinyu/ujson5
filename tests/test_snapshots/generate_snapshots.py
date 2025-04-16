"""Generate snapshots for snapshot tests. If you want to update the snapshots, run this script.
Snapshot tests are used to test the consistency of the dump and load functions.
"""

import snapshots  # type: ignore

import ujson5


def dump_composite_examples() -> None:
    """Dump json5 for alpha obj."""
    with open(
        snapshots.SNAPSHOTS_ROOT
        / snapshots.SNAPSHOT_NAMES["composite_example_default"],
        "w",
        encoding="utf8",
    ) as file:
        ujson5.dump(snapshots.COMPOSITE_EXAMPLE, file)

    with open(
        snapshots.SNAPSHOTS_ROOT
        / snapshots.SNAPSHOT_NAMES["composite_example_with_comments"],
        "w",
        encoding="utf8",
    ) as file:
        ujson5.dump(
            snapshots.COMPOSITE_EXAMPLE,
            file,
            snapshots.Human,
            indent=snapshots.DEFAULT_INDENT,
        )
    with open(
        snapshots.SNAPSHOTS_ROOT
        / snapshots.SNAPSHOT_NAMES["composite_example_no_comments"],
        "w",
        encoding="utf8",
    ) as file:
        ujson5.dump(snapshots.COMPOSITE_EXAMPLE, file, indent=snapshots.DEFAULT_INDENT)

    with open(
        snapshots.SNAPSHOTS_ROOT
        / snapshots.SNAPSHOT_NAMES["composite_example_no_indent"],
        "w",
        encoding="utf8",
    ) as file:
        ujson5.dump(snapshots.COMPOSITE_EXAMPLE, file)

    with open(
        snapshots.SNAPSHOTS_ROOT
        / snapshots.SNAPSHOT_NAMES["composite_example_7_indent"],
        "w",
        encoding="utf8",
    ) as file:
        ujson5.dump(snapshots.COMPOSITE_EXAMPLE, file, indent=7)

    with open(
        snapshots.SNAPSHOTS_ROOT
        / snapshots.SNAPSHOT_NAMES["composite_example_special_separators"],
        "w",
        encoding="utf8",
    ) as file:
        ujson5.dump(
            snapshots.COMPOSITE_EXAMPLE,
            file,
            indent=snapshots.DEFAULT_INDENT,
            separators=("|", "->"),
        )

    with open(
        snapshots.SNAPSHOTS_ROOT
        / snapshots.SNAPSHOT_NAMES["composite_example_with_trailing_comma"],
        "w",
        encoding="utf8",
    ) as file:
        ujson5.dump(
            snapshots.COMPOSITE_EXAMPLE,
            file,
            indent=snapshots.DEFAULT_INDENT,
            trailing_comma=True,
        )

    with open(
        snapshots.SNAPSHOTS_ROOT
        / snapshots.SNAPSHOT_NAMES["composite_example_no_trailing_comma"],
        "w",
        encoding="utf8",
    ) as file:
        ujson5.dump(
            snapshots.COMPOSITE_EXAMPLE,
            file,
            indent=snapshots.DEFAULT_INDENT,
            trailing_comma=False,
        )


def dump_pydantic_examples() -> None:
    """Dump json5 for pydantic obj."""
    with open(
        snapshots.SNAPSHOTS_ROOT / snapshots.SNAPSHOT_NAMES["pydantic_example"],
        "w",
        encoding="utf8",
    ) as file:
        ujson5.dump(
            snapshots.PYDANTIC_EXAMPLE.model_dump(),
            file,
            snapshots.CameraSlice,
            indent=snapshots.DEFAULT_INDENT,
        )


if __name__ == "__main__":
    snapshots.SNAPSHOTS_ROOT.mkdir(exist_ok=True)
    dump_composite_examples()
    dump_pydantic_examples()
    print("Snapshots generated successfully. 🎉")
