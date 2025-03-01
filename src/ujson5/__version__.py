"""The `version` module holds the version information for Pydantic."""

__all__ = ["VERSION"]

VERSION = "0.0.1a"
"""The version of ujson5."""


def version_short() -> str:
    """Return the `major.minor` part of ujson5 version.

    It returns '2.1' if ujson5 version is '2.1.1'.
    """
    return ".".join(VERSION.split(".")[:2])
