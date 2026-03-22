from pathlib import Path
from skills.core.engine.transition import check_transition
from skills.core.engine.schema import load_schemas

KB_DIR = Path(__file__).resolve().parents[4]
SKILLS_DIR = KB_DIR / "internals"


def test_valid_project_transition():
    schemas = load_schemas(SKILLS_DIR)
    ok, msg = check_transition("project", "active", "paused", schemas)
    assert ok is True


def test_invalid_project_transition():
    schemas = load_schemas(SKILLS_DIR)
    ok, msg = check_transition("project", "active", "exploring", schemas)
    assert ok is False
    assert "paused" in msg or "completed" in msg  # should list valid targets


def test_inbox_valid_transition():
    schemas = load_schemas(SKILLS_DIR)
    ok, msg = check_transition("inbox-item", "new", "incubating", schemas)
    assert ok is True


def test_inbox_invalid_transition():
    schemas = load_schemas(SKILLS_DIR)
    ok, msg = check_transition("inbox-item", "new", "promoted", schemas)
    assert ok is False


def test_terminal_state_has_no_transitions():
    schemas = load_schemas(SKILLS_DIR)
    ok, msg = check_transition("project", "archived", "active", schemas)
    assert ok is False


def test_unknown_type():
    schemas = load_schemas(SKILLS_DIR)
    ok, msg = check_transition("nonexistent", "a", "b", schemas)
    assert ok is False


def test_research_exploring_to_active():
    schemas = load_schemas(SKILLS_DIR)
    ok, msg = check_transition("research", "exploring", "active", schemas)
    assert ok is True
