# iorlas-kay

Kay (K) — personal knowledge base skills for Claude Code. Capture thoughts, observe capability gaps, and triage everything into structured knowledge.

Replaces `iorlas-inbox` and `iorlas-learn`.

## Skills

### `/inbox` — Universal Capture

Dump thoughts, tasks, links, voice transcripts. They become structured inbox files with auto-detected types and project context.

### `/reflect` — Observation Capture

Capture what broke, what was missing, or what you learned during a session. Observations land in the Inbox tagged with capability hints for structured triage.

### `/triage` — Inbox Triage

Process new inbox items: resolve mentions, link entities, update status. For observations: assess root cause, route to capability patches or personal patterns.

### `/consolidate` — Discover, Propose, Merge

Find scattered entities that belong together and consolidate them into living guides.

### `/init` — Kay Init

Set up folder structure, QMD semantic search, and MCP server. Run once before using other skills.

## Install

Add to your marketplace or install via `--plugin-dir`:

```bash
claude --plugin-dir /path/to/iorlas-kay
```

## Development

Clone and load from your local copy:

```bash
git clone https://github.com/iorlas/iorlas-kay.git
claude --plugin-dir ./iorlas-kay
```

Edit skills in `skills/`, then run `/reload-plugins` inside Claude Code to pick up changes. No restart needed.

## License

MIT — Denis Tomilin
