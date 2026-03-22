"""Validation engine — checks entity files against their type schemas."""
from dataclasses import dataclass
from pathlib import Path

from skills.core.engine.frontmatter import parse_frontmatter
from skills.core.engine.schema import TypeSchema


@dataclass
class Finding:
    level: str  # "ERROR" or "WARN"
    path: Path
    message: str

    def __str__(self):
        # Try to show a short relative path
        name = str(self.path)
        for parent in self.path.parents:
            if parent.name in ("Inbox", "Projects", "Researches", "People", "Companies", "Processes", "References", "Calls"):
                try:
                    name = str(self.path.relative_to(parent.parent))
                except ValueError:
                    pass
                break
        return f"{self.level:5s} {name}: {self.message}"


def validate_file(path: Path, schema: TypeSchema, model: type) -> list[Finding]:
    """Validate a single entity file against its schema."""
    findings: list[Finding] = []

    if not path.exists():
        findings.append(Finding("ERROR", path, "file does not exist"))
        return findings

    text = path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)

    if fm is None:
        findings.append(Finding("ERROR", path, "no valid YAML frontmatter found"))
        return findings

    # Check kind value
    actual_kind = str(fm.get("kind", "")).strip()
    if schema.kind_value and actual_kind != schema.kind_value:
        findings.append(Finding("ERROR", path, f"kind is '{actual_kind}', expected '{schema.kind_value}'"))

    # Check status validity
    if schema.status_lifecycle:
        actual_status = str(fm.get("status", "")).strip()
        valid_statuses = set(schema.status_lifecycle.keys())
        for targets in schema.status_lifecycle.values():
            valid_statuses.update(targets)
        if actual_status and actual_status not in valid_statuses:
            findings.append(Finding("ERROR", path, f"status '{actual_status}' not valid. Valid: {sorted(valid_statuses)}"))

    # Validate against Pydantic model
    try:
        model.model_validate(fm)
    except Exception as e:
        for error in getattr(e, "errors", lambda: [{"msg": str(e)}])():
            loc = ".".join(str(l) for l in error.get("loc", []))
            msg = error.get("msg", str(error))
            findings.append(Finding("ERROR", path, f"field '{loc}': {msg}"))

    return findings
