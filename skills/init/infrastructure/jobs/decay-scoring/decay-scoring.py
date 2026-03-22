#!/usr/bin/env python3
"""Decay Scoring — background metadata enrichment.

Writes decay_score into entity frontmatter. Not a user-facing report.

Usage:
    python3 skills/core/jobs/decay-scoring/decay-scoring.py [--verbose]
"""
import math
import sys
from datetime import datetime, date
from pathlib import Path

KNOWLEDGE_DIR = Path.home() / "Documents" / "Knowledge"
SKILLS_DIR = KNOWLEDGE_DIR / "skills"
TODAY = date.today()
VERBOSE = "--verbose" in sys.argv

# Import from KE engine
sys.path.insert(0, str(SKILLS_DIR / "core" / "engine"))
from frontmatter import parse_frontmatter, write_frontmatter
from schema import load_schemas


# Decay rates per kind — how fast entities lose relevance
# Lower λ = slower decay (people persist, inbox items fade fast)
DECAY_RATES = {
    "inbox": 0.05,
    "person": 0.005,
    "project": 0.02,
    "company": 0.01,
    "process": 0.01,
    "reference": 0.005,
    "research": 0.015,
}
DEFAULT_DECAY_RATE = 0.03


_warned_kinds = set()

def get_lambda(kind: str) -> float:
    if kind and kind not in DECAY_RATES and kind not in _warned_kinds:
        _warned_kinds.add(kind)
        print(f"  WARN: no decay rate for kind '{kind}', using default {DEFAULT_DECAY_RATE}")
    return DECAY_RATES.get(kind, DEFAULT_DECAY_RATE)


def main():
    updated = 0
    mtime_warns = 0

    # Derive entity folders from schemas — no hardcoded list
    schemas = load_schemas(SKILLS_DIR)
    dirs = sorted({s.folder for s in schemas.values() if s.folder})

    for dirname in dirs:
        dirpath = KNOWLEDGE_DIR / dirname
        if not dirpath.is_dir():
            continue
        legacy_files = sorted(dirpath.glob("*.md"))
        folder_files = sorted(dirpath.glob("*/README.md"))
        for f in legacy_files + folder_files:
            if f.name == "INDEX.md":
                continue

            text = f.read_text(encoding="utf-8")
            fm, body = parse_frontmatter(text)
            if fm is None:
                continue

            updated_str = fm.get("updated") or fm.get("created")
            if updated_str is None:
                continue
            if isinstance(updated_str, date):
                updated_date = updated_str
            else:
                try:
                    updated_date = datetime.strptime(str(updated_str)[:10], "%Y-%m-%d").date()
                except ValueError:
                    continue

            status = str(fm.get("status", "")).strip().lower()
            if status == "archived":
                continue

            kind = str(fm.get("kind", "") or fm.get("type", "")).strip().lower()
            base = float(fm.get("relevance_score", 1.0))

            days = (TODAY - updated_date).days
            lam = get_lambda(kind)
            score = round(base * math.exp(-lam * days), 2)

            fm["decay_score"] = score
            f.write_text(write_frontmatter(fm, body), encoding="utf-8")
            updated += 1

            # Detect mtime drift
            file_mtime = f.stat().st_mtime
            updated_ts = datetime.combine(updated_date, datetime.min.time()).timestamp()
            mtime_days = int((file_mtime - updated_ts) / 86400)
            if mtime_days > 1:
                if VERBOSE:
                    print(f"  MTIME-DRIFT: {dirname}/{f.name} — file modified {mtime_days}d after 'updated' field")
                mtime_warns += 1

            if VERBOSE:
                print(f"  {dirname}/{f.name}: decay_score={score:.2f} ({days}d, λ={lam})")

    print(f"Health check complete: {updated} entities scored, {mtime_warns} mtime warnings")


if __name__ == "__main__":
    main()
