"""This module contains shared variables and functions for the release scripts."""

import subprocess
from pathlib import Path


def run_command(*args: str) -> str:
    """Run a shell command and return the output."""
    p = subprocess.run(args, stdout=subprocess.PIPE, check=True, encoding="utf-8")
    return p.stdout.strip()


REPO = "austinyu/ujson5"
CHANGELOG_PATH = Path(__file__).parent.parent / "CHANGELOG.md"
PACKAGE_VERSION_PATH = (
    Path(__file__).parent.parent / "src" / "ujson5" / "__version__.py"
)
GITHUB_TOKEN = run_command("gh", "auth", "token")
