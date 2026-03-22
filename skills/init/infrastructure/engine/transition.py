"""Status transition engine — enforces lifecycle state machine per type."""
from datetime import date
from pathlib import Path

from skills.core.engine.frontmatter import parse_frontmatter, write_frontmatter
from skills.core.engine.schema import TypeSchema, resolve_schema_for_path, load_schemas


def check_transition(
    type_name: str,
    current_status: str,
    new_status: str,
    schemas: dict[str, TypeSchema],
) -> tuple[bool, str]:
    """Check if a status transition is valid. Returns (ok, message)."""
    schema = schemas.get(type_name)
    if not schema:
        return False, f"Unknown type '{type_name}'"
    if not schema.status_lifecycle:
        return True, "No lifecycle defined"
    allowed = schema.status_lifecycle.get(current_status, [])
    if new_status in allowed:
        return True, f"{current_status} -> {new_status}"
    return False, f"Cannot transition from '{current_status}' to '{new_status}'. Valid targets: {allowed}"


def transition_file(
    path: Path,
    new_status: str,
    kb_dir: Path,
    skills_dir: Path,
) -> str:
    """Transition an entity's status. Returns success message or raises ValueError."""
    schemas = load_schemas(skills_dir)
    schema = resolve_schema_for_path(path.resolve(), schemas)
    if not schema:
        raise ValueError(f"Cannot determine type for {path}")

    text = path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    if fm is None:
        raise ValueError(f"No frontmatter in {path}")

    current = str(fm.get("status", "")).strip()
    ok, msg = check_transition(schema.name, current, new_status, schemas)
    if not ok:
        raise ValueError(msg)

    fm["status"] = new_status
    fm["updated"] = date.today().isoformat()
    path.write_text(write_frontmatter(fm, body), encoding="utf-8")
    return f"{path.name}: {current} -> {new_status}"
