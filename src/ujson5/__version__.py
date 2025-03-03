"""The `version` module holds the version information for ujson5."""

__all__ = ["VERSION"]

VERSION = "0.0.1a"
"""The version of ujson5."""


def version_short() -> str:
    """Return the `major.minor` part of ujson5 version.

    It returns '2.1' if ujson5 version is '2.1.1'.
    """
    return ".".join(VERSION.split(".")[:2])


def version_info() -> str:
    """Return complete version information for ujson5 and its dependencies."""
    import platform  # pylint: disable=C0415
    import sys  # pylint: disable=C0415

    info = {
        "ujson5 version": VERSION,
        "python version": sys.version,
        "platform": platform.platform(),
    }
    return "\n".join(
        "{:>30} {}".format(k + ":", str(v).replace("\n", " ")) for k, v in info.items()
    )
