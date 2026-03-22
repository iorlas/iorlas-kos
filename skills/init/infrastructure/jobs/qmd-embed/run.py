#!/usr/bin/env python3
"""QMD Embed — re-index knowledge base for semantic search."""
CADENCE = 1800  # 30 minutes

import hashlib
import subprocess
import sys
from pathlib import Path

KNOWLEDGE_PATH = Path.home() / "Documents" / "Knowledge"
MARKER = Path(__file__).parent / ".last-embed-hash"


def get_fingerprint() -> str:
    """HEAD SHA + uncommitted .md changes as fingerprint."""
    try:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(KNOWLEDGE_PATH), capture_output=True, text=True
        ).stdout.strip()
        diff = subprocess.run(
            ["git", "diff", "--name-only", "HEAD", "--", "*.md"],
            cwd=str(KNOWLEDGE_PATH), capture_output=True, text=True
        ).stdout.strip()
        return hashlib.md5(f"{head}\n{diff}".encode()).hexdigest()
    except Exception:
        return ""


def main():
    current_hash = get_fingerprint()

    # Skip if nothing changed
    if MARKER.exists():
        try:
            if MARKER.read_text().strip() == current_hash:
                return 0
        except OSError:
            pass

    result = subprocess.run(
        ["npx", "@tobilu/qmd", "embed"],
        cwd=str(KNOWLEDGE_PATH)
    )

    if result.returncode != 0:
        return 1

    MARKER.write_text(current_hash)
    return 0


if __name__ == "__main__":
    sys.exit(main())
