"""Test the version of the package."""

import importlib

import ujson5


def test_version_consistency():
    """Test that the version in the package is consistent with the version in the metadata."""
    assert ujson5.__version__ == importlib.metadata.version("ujson5")
