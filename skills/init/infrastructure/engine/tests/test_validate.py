import tempfile
from pathlib import Path

from skills.core.engine.validate import validate_file, Finding
from skills.core.engine.schema import load_schemas, build_pydantic_model

KB_DIR = Path(__file__).resolve().parents[4]
SKILLS_DIR = KB_DIR / "skills"


def _write_temp(content: str, dir_name: str = "Projects", file_name: str = "README.md") -> Path:
    """Create a temp entity file in a directory matching schema dispatch."""
    tmp = Path(tempfile.mkdtemp())
    entity_dir = tmp / dir_name / "test-entity"
    entity_dir.mkdir(parents=True)
    f = entity_dir / file_name
    f.write_text(content, encoding="utf-8")
    return f


def _write_temp_inbox(content: str) -> Path:
    tmp = Path(tempfile.mkdtemp())
    inbox_dir = tmp / "Inbox"
    inbox_dir.mkdir(parents=True)
    f = inbox_dir / "I0001-test.md"
    f.write_text(content, encoding="utf-8")
    return f


def test_validate_valid_project():
    f = _write_temp("---\nkind: project\nid: '099'\nname: Test\nstatus: active\ncreated: 2026-03-14\nupdated: 2026-03-14\n---\n\n# Test")
    schemas = load_schemas(SKILLS_DIR)
    schema = schemas["project"]
    model = build_pydantic_model(schema)
    findings = validate_file(f, schema, model)
    errors = [x for x in findings if x.level == "ERROR"]
    assert len(errors) == 0


def test_validate_missing_frontmatter():
    f = _write_temp("Just a plain file.")
    schemas = load_schemas(SKILLS_DIR)
    schema = schemas["project"]
    model = build_pydantic_model(schema)
    findings = validate_file(f, schema, model)
    errors = [x for x in findings if x.level == "ERROR"]
    assert len(errors) > 0
    assert any("frontmatter" in e.message.lower() for e in errors)


def test_validate_wrong_kind_value():
    f = _write_temp_inbox("---\nkind: Idea\nid: I0001\nname: Test\nstatus: new\ncreated: 2026-03-14\n---\n")
    schemas = load_schemas(SKILLS_DIR)
    schema = schemas["inbox-item"]
    model = build_pydantic_model(schema)
    findings = validate_file(f, schema, model)
    kind_errors = [x for x in findings if x.level == "ERROR" and "kind" in x.message.lower()]
    assert len(kind_errors) > 0


def test_validate_correct_kind_no_error():
    f = _write_temp_inbox("---\nkind: inbox\nid: I0001\nname: Test\nstatus: new\ncreated: 2026-03-14\n---\n")
    schemas = load_schemas(SKILLS_DIR)
    schema = schemas["inbox-item"]
    model = build_pydantic_model(schema)
    findings = validate_file(f, schema, model)
    kind_errors = [x for x in findings if x.level == "ERROR" and "kind" in x.message.lower()]
    assert len(kind_errors) == 0


def test_validate_invalid_status():
    f = _write_temp("---\nkind: project\nid: '099'\nname: Test\nstatus: exploring\ncreated: 2026-03-14\n---\n")
    schemas = load_schemas(SKILLS_DIR)
    schema = schemas["project"]
    model = build_pydantic_model(schema)
    findings = validate_file(f, schema, model)
    status_errors = [x for x in findings if x.level == "ERROR" and "status" in x.message.lower()]
    assert len(status_errors) > 0


def test_validate_valid_status():
    f = _write_temp("---\nkind: project\nid: '099'\nname: Test\nstatus: paused\ncreated: 2026-03-14\n---\n")
    schemas = load_schemas(SKILLS_DIR)
    schema = schemas["project"]
    model = build_pydantic_model(schema)
    findings = validate_file(f, schema, model)
    status_errors = [x for x in findings if x.level == "ERROR" and "status" in x.message.lower()]
    assert len(status_errors) == 0


def test_finding_str_format():
    f = Finding("ERROR", Path("/some/Projects/test/README.md"), "test message")
    s = str(f)
    assert "ERROR" in s
    assert "test message" in s
