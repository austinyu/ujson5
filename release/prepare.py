"""Automate the version bump and changelog update process."""

# mypy: disable-error-code="import-untyped"

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

import requests
from shared import (
    CHANGELOG_PATH,
    GITHUB_TOKEN,
    PACKAGE_VERSION_PATH,
    REPO,
    run_command,
)

ROOT_DIR = Path(__file__).parent.parent


def get_previous_version() -> str:
    """Get the latest git tag from the repository."""
    tags = run_command("git", "tag").splitlines()
    if not tags:
        print("No git tags found. Please ensure the repository has tags.")
        sys.exit(1)
    return tags[-1].lstrip("v")  # Remove the leading "v" if present


def update_version(new_version: str) -> str:
    """Update the version in the giving py version file.
    Note that both the arg `new_version` and the version in the file should be in the format
    "X.Y.Z" without the leading "v". The leading "v" will be added automatically.

    Args:
        new_version (str): The new version to set.

    Returns:
        str: The old version.
    """
    with open(PACKAGE_VERSION_PATH, encoding="utf8") as f:
        content = f.read()

    # Regex to match the VERSION assignment
    pattern = r"(VERSION\s*=\s*)([\'\"])(v[^\"^\']+)([\'\"])"
    version_stm = re.search(pattern, content)
    if not version_stm:
        print(
            "Could not find the version assignment in the version file."
            'Please make sure the version file has a line like `VERSION = "v1.2.3"`.'
        )
        sys.exit(1)
    old_version = version_stm.group(3)
    old_version_stm = "".join(version_stm.groups())
    new_version_stm = old_version_stm.replace(old_version, f"v{new_version}")
    with open(PACKAGE_VERSION_PATH, "w", encoding="utf8") as f:
        new_content = content.replace(old_version_stm, new_version_stm)
        f.write(new_content)
    return old_version[1:]  # Remove the leading "v" from the version string


def get_notes(new_version: str) -> str:
    """Fetch auto-generated release notes from github.

    Args:
        new_version (str): The new version to set. Version without the leading "v".

    Returns:
        str: The release notes.
    """
    new_version = f"v{new_version}"
    last_tag = run_command("git", "describe", "--tags", "--abbrev=0")
    auth_token = GITHUB_TOKEN

    data = {
        "target_committish": "main",
        "previous_tag_name": last_tag,
        "tag_name": new_version,
    }
    response = requests.post(
        f"https://api.github.com/repos/{REPO}/releases/generate-notes",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {auth_token}",
            "x-github-api-version": "2022-11-28",
        },
        data=json.dumps(data),
        timeout=100,
    )
    response.raise_for_status()

    body = response.json()["body"]

    body = body.replace(
        "<!-- Release notes generated using configuration "
        + "in .github/release.yml at main -->\n\n",
        "",
    )

    # Add one level to all headers so they match HISTORY.md, and add trailing newline
    body = re.sub(pattern="^(#+ .+?)$", repl=r"#\1\n", string=body, flags=re.MULTILINE)

    # Ensure a blank line before headers
    body = re.sub(pattern="([^\n])(\n#+ .+?\n)", repl=r"\1\n\2", string=body)

    # Render PR links nicely
    body = re.sub(
        pattern=f"https://github.com/{REPO}/pull/(\\d+)",
        repl=f"[#\\1](https://github.com/{REPO}/pull/\\1)",
        string=body,
    )

    # Remove "full changelog" link
    body = re.sub(
        pattern=r"\*\*Full Changelog\*\*: https://.*$",
        repl="",
        string=body,
    )

    return body.strip()


def update_changelog(old_version: str, new_version: str) -> None:
    """Generate release notes and prepend them to HISTORY.md.
    Both versions should be in the format "X.Y.Z" without the leading "v".

    Args:
        old_version (str): The old version.
        new_version (str): The new version to set.
    """
    changelog_content = CHANGELOG_PATH.read_text(encoding="utf8")

    date_today_str = f"{date.today():%Y-%m-%d}"
    title = f"v{new_version} ({date_today_str})"
    notes = get_notes(new_version)
    new_chunk = (
        "<!-- markdownlint-disable MD024 -->\n\n"
        f"## {title}\n\n"
        f"[GitHub release](https://github.com/{REPO}/releases/tag/v{new_version})\n\n"
        f"{notes}\n\n"
        "[**Full Changelog**](https://github.com/austinyu/ujson5/compare"
        f"/v{old_version}...v{new_version})\n\n"
    )

    fst_new_line = changelog_content.find("\n")
    changelog_content = new_chunk + changelog_content[fst_new_line + 1 :]
    CHANGELOG_PATH.write_text(changelog_content)

    run_command("pre-commit", "run", "trunk-fmt")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # For easier iteration, can generate the release notes without saving
    parser.add_argument("version", help="New version number to release.")
    args = parser.parse_args()

    version = args.version

    if not re.match(r"^\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?$", version):
        print(
            'Version number should be in the format "X.Y.Z" or "X.Y.Z-alpha".'
            + f" New version: {version}.\n"
        )
        sys.exit(1)

    old_v = get_previous_version()
    print(f"📄 Version file updated to v{version}.")
    run_command("uv", "lock", "-P", "ujson5")
    print("🔒 Dependencies locked.")
    update_changelog(old_v, version)
    print(f"📜 Changelog updated with release notes for v{version}.")
