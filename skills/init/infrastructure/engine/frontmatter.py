"""Frontmatter utilities for Knowledge Engine.

Absorbed from _meta/frontmatter_util.py and _meta/kb-audit.py.
"""
import re
from pathlib import Path

import yaml


def parse_frontmatter(text: str) -> tuple[dict | None, str]:
    """Parse YAML frontmatter from markdown text.

    Returns (frontmatter_dict, body) where body is everything after closing ---.
    Returns (None, text) if no valid frontmatter found.
    """
    if not text.startswith("---"):
        return None, text
    end = text.find("\n---", 3)
    if end == -1:
        return None, text
    yaml_str = text[4:end]
    body = text[end + 4:]
    fm = yaml.safe_load(yaml_str)
    if not isinstance(fm, dict):
        return None, text
    return fm, body


def write_frontmatter(fm: dict, body: str) -> str:
    """Serialize frontmatter dict + body back to markdown."""
    yaml_str = yaml.dump(fm, default_flow_style=False, allow_unicode=True, sort_keys=False)
    yaml_str = yaml_str.rstrip("\n")
    return f"---\n{yaml_str}\n---{body}"


def update_file_frontmatter(filepath: Path, updates: dict) -> bool:
    """Read a file, update frontmatter fields, write back. Returns True on success."""
    text = filepath.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    if fm is None:
        return False
    fm.update(updates)
    filepath.write_text(write_frontmatter(fm, body), encoding="utf-8")
    return True


def extract_wikilinks(text: str) -> list[str]:
    """Return all [[target]] strings from text (body + frontmatter)."""
    matches = re.findall(r"\[\[([^\]\n]{1,200})\]\]", text)
    return matches


def slugify(name: str) -> str:
    """Lowercase, strip punctuation, collapse spaces for loose matching."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
