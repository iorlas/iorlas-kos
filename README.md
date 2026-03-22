# Kay

Personal knowledge base for Claude Code. One plugin, one command, everything set up.

## Get Started

```bash
# 1. Add marketplace
claude plugin marketplace add https://github.com/iorlas/iorlas-marketplace.git

# 2. Install Kay
claude plugin install iorlas-kay@iorlas-marketplace

# 3. Run init (this sets up everything)
/init
```

That's it. Init will:
- Check dependencies (Node.js, Python, QMD, jq, git)
- Create your Knowledge folder with ontology-driven structure
- Install the entity engine, scheduler, and background jobs
- Configure semantic search (QMD), memory, MCP, and a status line
- Tell you what to do next

Run `/init` again anytime — it detects drift and self-heals.

## After Setup

**Start the scheduler** in a spare terminal tab (keeps embeddings fresh, runs decay scoring, incubates new ideas):

```bash
python3 ~/Documents/Knowledge/skills/core/scheduler.py
```

**Start working** from your Knowledge folder:

```bash
cd ~/Documents/Knowledge
claude
```

## Skills

| Command | What it does |
|---------|-------------|
| `/init` | Set up from scratch or health-check an existing install |
| `/inbox` | Capture thoughts, tasks, links, voice dumps — from any directory |
| `/reflect` | Record what broke or what you learned during a session |
| `/triage` | Process inbox items: resolve mentions, link entities, route observations |
| `/consolidate` | Find scattered entities that belong together and merge them |

## How It Works

Kay is **ontology-driven**. Entity schemas (YAML files in the plugin) define your knowledge structure:

- **Inbox** — captured ideas, links, notes awaiting triage
- **Projects** — delivery work, consulting, content creation
- **People** — contacts, collaborators, public figures
- **Companies** — organizations relevant to your work
- **Researches** — deep investigations with sources and analysis
- **Processes** — reusable methodologies and workflows
- **References** — curated resource lists by domain

Add a new `.yaml` schema to the plugin's `ontology/` folder, rerun `/init`, and the new entity type appears.

## Extending

Want a new entity type? Create a schema:

```yaml
# ontology/book.yaml
name: book
description: Books you've read or want to read
folder: Books
file_pattern: "{slug}/README.md"
inherits: base
```

Run `/init` — Kay creates the `Books/` folder and you're ready to go.

## Development

```bash
git clone https://github.com/iorlas/iorlas-kay.git
claude --plugin-dir ./iorlas-kay
```

Use `--plugin-dir` for local development. Edits are picked up on session start — no cache issues.

## License

MIT — Denis Tomilin
