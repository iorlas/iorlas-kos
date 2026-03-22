#!/usr/bin/env python3
"""Decay Scoring — compute relevance decay for all entities."""
CADENCE = 86400  # 24 hours

import subprocess
import sys
from pathlib import Path

KNOWLEDGE_PATH = Path.home() / "Documents" / "Knowledge"
SCRIPT_DIR = Path(__file__).parent
LOG_FILE = SCRIPT_DIR / "last-run.log"


def main():
    # Find venv python or fall back to system
    venv_py = KNOWLEDGE_PATH / "internals" / ".venv" / "bin" / "python3"
    if not venv_py.exists():
        venv_py = KNOWLEDGE_PATH / "internals" / ".venv" / "Scripts" / "python.exe"
    py = str(venv_py) if venv_py.exists() else sys.executable

    # Run decay scoring
    with open(LOG_FILE, "a") as log:
        result = subprocess.run(
            [py, str(SCRIPT_DIR / "decay-scoring.py"), "--verbose"],
            stdout=log, stderr=log
        )

    if result.returncode != 0:
        return result.returncode

    # Auto-commit decay score changes
    subprocess.run(
        ["git", "add", "-A", "--", "*.md"],
        cwd=str(KNOWLEDGE_PATH)
    )
    # Only commit if there are staged changes
    check = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=str(KNOWLEDGE_PATH)
    )
    if check.returncode != 0:
        subprocess.run(
            ["git", "commit", "-m", "chore: update decay scores (automated)"],
            cwd=str(KNOWLEDGE_PATH)
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
