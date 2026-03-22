"""Entity creation — bootstrap new entities from templates with valid frontmatter."""
from datetime import date
from pathlib import Path

from filelock import FileLock

from skills.core.engine.frontmatter import parse_frontmatter, slugify
from skills.core.engine.registry import EntityRegistry
from skills.core.engine.schema import TypeSchema, build_pydantic_model, load_schemas


def create_entity(type_name: str, name: str, kb_dir: Path, skills_dir: Path) -> Path:
    """Create a new entity. Returns the created file path."""
    schemas = load_schemas(skills_dir)
    if type_name not in schemas:
        raise ValueError(f"Unknown type '{type_name}'. Valid: {sorted(schemas.keys())}")

    schema = schemas[type_name]
    slug = slugify(name)
    today = date.today().isoformat()

    # Allocate ID under lock to prevent race conditions
    lock = FileLock(str(skills_dir / "core" / ".ke.lock"), timeout=30)
    with lock:
        registry = EntityRegistry(kb_dir)
        registry.build()

        if type_name == "inbox-item":
            entity_id = registry.next_inbox_id()
        else:
            entity_id = registry.next_id()

        # Build target path
        folder = kb_dir / schema.folder
        if "README.md" in schema.file_pattern:
            entity_dir = folder / f"{entity_id}-{slug}"
            entity_dir.mkdir(parents=True, exist_ok=True)
            target = entity_dir / "README.md"
        else:
            folder.mkdir(parents=True, exist_ok=True)
            target = folder / f"{entity_id}-{slug}.md"

        # Load and fill template
        template_content = _load_template(type_name, skills_dir)
        content = template_content.replace("{id}", entity_id)
        content = content.replace("{name}", name)
        content = content.replace("{slug}", slug)
        content = content.replace("{created}", today)

        # Validate before writing (eat our own dog food)
        fm, body = parse_frontmatter(content)
        if fm:
            model = build_pydantic_model(schema)
            model.model_validate(fm)

        target.write_text(content, encoding="utf-8")

    return target


def _load_template(type_name: str, skills_dir: Path) -> str:
    """Find and load template for the given type."""
    # Search all skill folders for matching template
    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        templates_dir = skill_dir / "templates"
        if not templates_dir.is_dir():
            continue
        # Try folder template: templates/{type_name}/README.md
        folder_template = templates_dir / type_name / "README.md"
        if folder_template.exists():
            return folder_template.read_text(encoding="utf-8")
        # Try single-file template: templates/{type_name}.md
        file_template = templates_dir / f"{type_name}.md"
        if file_template.exists():
            return file_template.read_text(encoding="utf-8")

    raise FileNotFoundError(f"No template found for type '{type_name}'")
