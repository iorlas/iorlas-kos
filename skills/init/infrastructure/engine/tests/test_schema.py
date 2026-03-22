from pathlib import Path
from skills.core.engine.schema import load_schemas, build_pydantic_model, resolve_schema_for_path

KB_DIR = Path(__file__).resolve().parents[4]
SKILLS_DIR = KB_DIR / "internals"


def test_load_schemas_finds_all_types():
    schemas = load_schemas(SKILLS_DIR)
    assert "inbox-item" in schemas
    assert "project" in schemas
    assert "research" in schemas
    assert "person" in schemas
    assert "company" in schemas
    assert "process" in schemas
    assert "reference" in schemas
    assert len(schemas) >= 7


def test_load_schema_inherits_base_fields():
    schemas = load_schemas(SKILLS_DIR)
    project = schemas["project"]
    # Base fields should be present
    assert "name" in project.fields
    assert "kind" in project.fields
    assert "status" in project.fields
    assert "created" in project.fields
    assert "id" in project.fields


def test_load_schema_has_type_specific_fields():
    schemas = load_schemas(SKILLS_DIR)
    inbox = schemas["inbox-item"]
    assert "source" in inbox.fields
    process = schemas["process"]
    assert "origin" in process.fields


def test_load_schema_overrides_apply():
    schemas = load_schemas(SKILLS_DIR)
    inbox = schemas["inbox-item"]
    # inbox overrides aliases to not required
    aliases_field = inbox.fields.get("aliases", {})
    assert aliases_field.get("required") == False


def test_build_pydantic_model_validates_valid_data():
    schemas = load_schemas(SKILLS_DIR)
    Model = build_pydantic_model(schemas["project"])
    instance = Model.model_validate({
        "kind": "project",
        "id": "050",
        "name": "Test Project",
        "status": "active",
        "created": "2026-03-14",
    })
    assert instance.name == "Test Project"


def test_build_pydantic_model_rejects_missing_required():
    schemas = load_schemas(SKILLS_DIR)
    Model = build_pydantic_model(schemas["project"])
    import pytest
    with pytest.raises(Exception):
        Model.model_validate({"kind": "project"})  # missing id, name, status, created


def test_build_pydantic_model_allows_extra_fields():
    """Pydantic model should allow extra fields (for claims, custom fields etc)."""
    schemas = load_schemas(SKILLS_DIR)
    Model = build_pydantic_model(schemas["project"])
    instance = Model.model_validate({
        "kind": "project",
        "id": "050",
        "name": "Test",
        "status": "active",
        "created": "2026-03-14",
        "some_custom_field": "hello",
    })
    assert instance.some_custom_field == "hello"


def test_resolve_schema_for_path_project():
    schemas = load_schemas(SKILLS_DIR)
    schema = resolve_schema_for_path(KB_DIR / "Projects" / "050-knowledge-os" / "README.md", schemas)
    assert schema is not None
    assert schema.name == "project"


def test_resolve_schema_for_path_inbox():
    schemas = load_schemas(SKILLS_DIR)
    schema = resolve_schema_for_path(KB_DIR / "Inbox" / "I0001-test.md", schemas)
    assert schema is not None
    assert schema.name == "inbox-item"


def test_resolve_schema_for_path_unknown():
    schemas = load_schemas(SKILLS_DIR)
    schema = resolve_schema_for_path(KB_DIR / "RandomFolder" / "file.md", schemas)
    assert schema is None
