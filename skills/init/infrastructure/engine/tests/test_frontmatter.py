from skills.core.engine.frontmatter import (
    parse_frontmatter,
    write_frontmatter,
    extract_wikilinks,
    slugify,
)


def test_parse_frontmatter_basic():
    text = "---\ntype: project\nname: Test\n---\n\n# Body"
    fm, body = parse_frontmatter(text)
    assert fm == {"type": "project", "name": "Test"}
    assert body.strip() == "# Body"


def test_parse_frontmatter_missing():
    text = "No frontmatter here"
    fm, body = parse_frontmatter(text)
    assert fm is None
    assert body == text


def test_write_frontmatter_roundtrip():
    fm = {"type": "project", "name": "Test"}
    body = "\n\n# Body\n"
    result = write_frontmatter(fm, body)
    fm2, body2 = parse_frontmatter(result)
    assert fm2 == fm
    assert body2 == body


def test_extract_wikilinks():
    text = "See [[Knowledge OS]] and [[Denis Tomilin]] for details."
    links = extract_wikilinks(text)
    assert links == ["Knowledge OS", "Denis Tomilin"]


def test_extract_wikilinks_in_yaml():
    text = "---\nentity: '[[Denis Tomilin]]'\n---\nBody"
    links = extract_wikilinks(text)
    assert "Denis Tomilin" in links


def test_slugify():
    assert slugify("Knowledge OS") == "knowledge-os"
    assert slugify("AI-Powered Research!") == "ai-powered-research"
