from pathlib import Path
from skills.core.engine.registry import EntityRegistry

KB_DIR = Path(__file__).resolve().parents[4]


def test_registry_builds():
    reg = EntityRegistry(KB_DIR)
    reg.build()
    assert len(reg.all_paths) > 0


def test_registry_resolve_by_name():
    reg = EntityRegistry(KB_DIR)
    reg.build()
    # "Personal Knowledge OS" should resolve (it's a known entity)
    result = reg.resolve("Personal Knowledge OS")
    assert result is not None


def test_registry_resolve_by_slug():
    reg = EntityRegistry(KB_DIR)
    reg.build()
    result = reg.resolve("knowledge-os")
    assert result is not None


def test_registry_resolve_unknown():
    reg = EntityRegistry(KB_DIR)
    reg.build()
    result = reg.resolve("Nonexistent Entity That Does Not Exist 12345")
    assert result is None


def test_registry_next_id():
    reg = EntityRegistry(KB_DIR)
    reg.build()
    next_id = reg.next_id()
    assert next_id.isdigit()
    assert len(next_id) == 3
    # Should be higher than any existing ID
    assert int(next_id) > 50  # we know IDs go up to at least 074


def test_registry_next_inbox_id():
    reg = EntityRegistry(KB_DIR)
    reg.build()
    next_id = reg.next_inbox_id()
    assert next_id.startswith("I")
    assert len(next_id) == 5  # I + 4 digits
    # Should be higher than any existing inbox ID
    assert int(next_id[1:]) > 30  # we know inbox IDs go up to at least I0034


def test_registry_indexes_inbox_items():
    reg = EntityRegistry(KB_DIR)
    reg.build()
    # There should be inbox items indexed
    has_inbox = any("Inbox" in str(p) for p in reg.all_paths)
    assert has_inbox
