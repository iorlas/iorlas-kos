# iorlas-kay

Kay (K) — personal knowledge base skills for Claude Code. Capture thoughts, observe capability gaps, and triage everything into structured knowledge.

Replaces `iorlas-inbox` and `iorlas-learn`.

## Quick Start

```bash
# 1. Add marketplace
claude plugin marketplace add https://github.com/iorlas/iorlas-marketplace.git

# 2. Install Kay
claude plugin install iorlas-kay@iorlas-marketplace

# 3. Start Claude Code and run init
/kay-init
```

## Skills

### `/kay-init` — Setup & Dependencies

Detects your OS, checks/installs dependencies, creates the Knowledge folder, configures QMD, MCP, and Obsidian. Run once to get started, safe to re-run anytime.

### `/kay-inbox` — Universal Capture

Dump thoughts, tasks, links, voice transcripts. They become structured inbox files with auto-detected types and project context.

### `/kay-reflect` — Observation Capture

Capture what broke, what was missing, or what you learned during a session. Observations land in the Inbox tagged with capability hints for structured triage.

### `/kay-triage` — Inbox Triage

Process new inbox items: resolve mentions, link entities, update status. For observations: assess root cause, route to capability patches or personal patterns.

### `/kay-consolidate` — Discover, Propose, Merge

Find scattered entities that belong together and consolidate them into living guides.

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
