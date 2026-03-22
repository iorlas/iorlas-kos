"""Link checker — finds broken wikilinks across the Knowledge Base."""
from pathlib import Path

from skills.core.engine.frontmatter import extract_wikilinks
from skills.core.engine.registry import EntityRegistry
from skills.core.engine.validate import Finding


def check_links(kb_dir: Path) -> list[Finding]:
    """Scan all markdown files for wikilinks and report those that don't resolve."""
    findings: list[Finding] = []
    registry = EntityRegistry(kb_dir)
    registry.build()

    # Collect all wikilinks across the KB
    link_sources: dict[str, list[Path]] = {}
    skip_dirs = {"_meta", "internals", ".claude", ".git", "Assets"}

    for md in sorted(kb_dir.rglob("*.md")):
        rel = md.relative_to(kb_dir)
        if any(part in skip_dirs for part in rel.parts):
            continue
        text = md.read_text(encoding="utf-8")
        for link in extract_wikilinks(text):
            link_sources.setdefault(link, []).append(md)

    # Check each unique link
    for link, sources in sorted(link_sources.items()):
        target = registry.resolve(link)
        if target is None:
            # Report phantom link from first source only (avoid spam)
            findings.append(Finding(
                "WARN", sources[0],
                f"phantom link [[{link}]] ({len(sources)} occurrence{'s' if len(sources) != 1 else ''})"
            ))

    return findings
