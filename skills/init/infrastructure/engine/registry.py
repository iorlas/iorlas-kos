"""Entity registry for the Knowledge Engine.

Indexes all entities for:
- Wikilink resolution (name/slug/path lookup)
- ID allocation (next available numeric ID)
"""
import re
from pathlib import Path

from skills.core.engine.frontmatter import parse_frontmatter, slugify

ENTITY_DIRS = ["Projects", "People", "Companies", "Processes", "References", "Researches", "Calls"]


class EntityRegistry:
    def __init__(self, kb_dir: Path):
        self.kb_dir = kb_dir
        # id_str → list of Paths (to detect duplicates)
        self.by_id: dict[str, list[Path]] = {}
        # name_lower → Path
        self.by_name: dict[str, Path] = {}
        # slug → Path
        self.by_slug: dict[str, Path] = {}
        # all indexed entity paths (README.md and inbox .md files)
        self.all_paths: list[Path] = []
        self._max_id: int = 0
        self._max_inbox_id: int = 0

    def build(self):
        """Scan and index all entities from folder-per-entity dirs and Inbox."""
        # Scan folder-per-entity dirs
        for dirname in ENTITY_DIRS:
            dirpath = self.kb_dir / dirname
            if not dirpath.is_dir():
                continue
            for entry in sorted(dirpath.iterdir()):
                if not entry.is_dir():
                    continue
                readme = entry / "README.md"
                if not readme.exists():
                    continue
                self._index_file(readme)
                # Track max ID from folder name prefix (e.g. "074-artisyn" → 74)
                m = re.match(r"^(\d+)-", entry.name)
                if m:
                    folder_id = int(m.group(1))
                    if folder_id > self._max_id:
                        self._max_id = folder_id

        # Scan Inbox
        inbox_dir = self.kb_dir / "Inbox"
        if inbox_dir.is_dir():
            for entry in sorted(inbox_dir.glob("I????-*.md")):
                if not entry.is_file():
                    continue
                self._index_file(entry)
                # Track max inbox ID from filename prefix (e.g. "I0032-..." → 32)
                m = re.match(r"^I(\d{4})-", entry.name)
                if m:
                    inbox_id = int(m.group(1))
                    if inbox_id > self._max_inbox_id:
                        self._max_inbox_id = inbox_id

    def _index_file(self, path: Path):
        """Parse frontmatter of a file and register it in the indexes."""
        self.all_paths.append(path)
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            return
        fm, _ = parse_frontmatter(text)
        if fm is None:
            return

        # Register by id
        entity_id = str(fm.get("id", "")).strip()
        if entity_id:
            self.by_id.setdefault(entity_id, []).append(path)

        # Register by name and aliases
        name = str(fm.get("name", "")).strip()
        if name:
            self.by_name[name.lower()] = path
            self.by_slug[slugify(name)] = path

        aliases = fm.get("aliases") or []
        if isinstance(aliases, str):
            aliases = [aliases]
        for alias in aliases:
            a = str(alias).strip()
            if a:
                self.by_name[a.lower()] = path
                self.by_slug[slugify(a)] = path

    def resolve(self, link: str) -> Path | None:
        """Try to resolve a wikilink string to an entity path.

        Tries in order:
        1. Exact name match (case-insensitive)
        2. Slug match
        3. Path-style link: "Projects/050-knowledge-os" → README.md
        4. Partial folder prefix match: "050-knowledge-os" or "050"
        """
        # 1. Exact name match
        hit = self.by_name.get(link.lower())
        if hit:
            return hit

        # 2. Slug match
        hit = self.by_slug.get(slugify(link))
        if hit:
            return hit

        # 3. Path-style link: "Projects/050-knowledge-os" → README.md
        try:
            candidate = self.kb_dir / link / "README.md"
            if candidate.exists():
                return candidate
        except OSError:
            pass

        # 4. Partial: folder name match or numeric prefix match
        for path in self.all_paths:
            parent = path.parent
            if parent.name == link or parent.name.startswith(link + "-"):
                return path

        return None

    def next_id(self) -> str:
        """Return the next available zero-padded 3-digit entity ID."""
        return f"{self._max_id + 1:03d}"

    def next_inbox_id(self) -> str:
        """Return the next available Inbox ID in the form I#### (4 digits)."""
        return f"I{self._max_inbox_id + 1:04d}"
