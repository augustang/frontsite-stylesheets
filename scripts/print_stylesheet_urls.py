#!/usr/bin/env python3
"""Print Super CSS Inject paste-ready URLs pinned to current git HEAD (jsDelivr + raw)."""
from __future__ import annotations

import os
import re
import subprocess
import sys

REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_GH = ("augustang", "frontsite-stylesheets")

SQUARESPACE_FILES = (
    "cta-test-1.css",
    "header-v1.css",
    "inject-probe.css",
)


def _git_rev_parse_head() -> str:
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()
        sys.exit(
            f"Not a git repo or git failed (run from clone with commits).\n{err}"
        )
    sha = proc.stdout.strip()
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        sys.exit(f"Unexpected git SHA: {sha!r}")
    return sha


def _remote_user_repo() -> tuple[str, str]:
    proc = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return DEFAULT_GH
    url = (proc.stdout or "").strip()
    # git@github.com:user/repo.git or https://github.com/user/repo.git
    m = re.search(r"github\.com[:/]([^/]+)/([^/.]+)", url)
    if m:
        return m.group(1), re.sub(r"\.git$", "", m.group(2))
    return DEFAULT_GH


def main() -> None:
    sha = _git_rev_parse_head()
    user, repo = _remote_user_repo()
    sha_short = sha[:7]

    print(f"# Git HEAD {sha}")
    print("# Paste into Super CSS Inject → Options (update after each push).\n")

    for name in SQUARESPACE_FILES:
        print(f"## {name}\n")
        print(
            "jsDelivr (full SHA):",
            f"https://cdn.jsdelivr.net/gh/{user}/{repo}@{sha}/squarespace/{name}",
        )
        print(
            "jsDelivr (7-char):  ",
            f"https://cdn.jsdelivr.net/gh/{user}/{repo}@{sha_short}/squarespace/{name}",
        )
        print(
            "Raw GitHub:           ",
            f"https://raw.githubusercontent.com/{user}/{repo}/{sha}/squarespace/{name}",
        )
        print()


if __name__ == "__main__":
    main()
