"""Generate snapshots for snapshot tests. If you want to update the snapshots, run this script.
Snapshot tests are used to test the consistency of the dump and load functions.
"""

import ujson5

from . import snapshots


def dump_alpha() -> None:
    """Dump json5 for alpha obj."""
    with open(
        snapshots.SNAPSHOTS_ROOT / snapshots.SNAPSHOT_NAMES["alpha_default"],
        "w",
        encoding="utf8",
    ) as file:
        ujson5.dump(snapshots.ALPHA, file)

    with open(
        snapshots.SNAPSHOTS_ROOT / snapshots.SNAPSHOT_NAMES["alpha_with_comments"],
        "w",
        encoding="utf8",
    ) as file:
        ujson5.dump(
            snapshots.ALPHA, file, snapshots.Human, indent=snapshots.DEFAULT_INDENT
        )
    with open(
        snapshots.SNAPSHOTS_ROOT / snapshots.SNAPSHOT_NAMES["alpha_no_comments"],
        "w",
        encoding="utf8",
    ) as file:
        ujson5.dump(snapshots.ALPHA, file, indent=snapshots.DEFAULT_INDENT)

    with open(
        snapshots.SNAPSHOTS_ROOT / snapshots.SNAPSHOT_NAMES["alpha_no_indent"],
        "w",
        encoding="utf8",
    ) as file:
        ujson5.dump(snapshots.ALPHA, file)

    with open(
        snapshots.SNAPSHOTS_ROOT / snapshots.SNAPSHOT_NAMES["alpha_7_indent"],
        "w",
        encoding="utf8",
    ) as file:
        ujson5.dump(snapshots.ALPHA, file, indent=7)

    with open(
        snapshots.SNAPSHOTS_ROOT / snapshots.SNAPSHOT_NAMES["alpha_special_separators"],
        "w",
        encoding="utf8",
    ) as file:
        ujson5.dump(
            snapshots.ALPHA,
            file,
            indent=snapshots.DEFAULT_INDENT,
            separators=("|", "->"),
        )

    with open(
        snapshots.SNAPSHOTS_ROOT
        / snapshots.SNAPSHOT_NAMES["alpha_with_trailing_comma"],
        "w",
        encoding="utf8",
    ) as file:
        ujson5.dump(
            snapshots.ALPHA,
            file,
            indent=snapshots.DEFAULT_INDENT,
            trailing_comma=True,
        )

    with open(
        snapshots.SNAPSHOTS_ROOT / snapshots.SNAPSHOT_NAMES["alpha_no_trailing_comma"],
        "w",
        encoding="utf8",
    ) as file:
        ujson5.dump(
            snapshots.ALPHA,
            file,
            indent=snapshots.DEFAULT_INDENT,
            trailing_comma=False,
        )


if __name__ == "__main__":
    dump_alpha()
