# Contributing to Kay

## Development Setup

Clone and use `--plugin-dir` for local development:

```bash
git clone https://github.com/iorlas/iorlas-kay.git
claude --plugin-dir ./iorlas-kay
```

Edits are picked up on session start. No cache, no symlinks, no stale files.

**Tip:** Add a shell alias for convenience:

```bash
# fish
alias c="claude --plugin-dir ~/Workspaces/iorlas-kay"

# bash/zsh
alias c="claude --plugin-dir ~/Workspaces/iorlas-kay"
```

## Project Structure

```
skills/
  init/
    SKILL.md              — init skill instructions
    dependencies.json     — required tools and install commands
    kay-statusline.sh     — status line script (copied to ~/.claude/hooks/)
    ontology/             — entity type schemas (YAML) — drives folder structure
    templates/            — entity templates (copied to Knowledge repo)
    infrastructure/       — engine, scheduler, jobs (copied to Knowledge repo)
  inbox/SKILL.md          — capture skill
  triage/SKILL.md         — triage skill
  reflect/SKILL.md        — observation capture skill
  consolidate/SKILL.md    — entity merging skill
```

## How Init Works

Init is ontology-driven. Each `.yaml` file in `ontology/` defines an entity type with a `folder` field. Init reads these and creates the corresponding directories in `~/Documents/Knowledge/`.

The `infrastructure/` directory contains the Python engine, scheduler, and background jobs. Init copies these into `~/Documents/Knowledge/internals/` on first run and detects drift on subsequent runs.

## Adding Entity Types

1. Create a new `.yaml` in `skills/init/ontology/`
2. Optionally add a template in `skills/init/templates/`
3. Run `/init` — the new folder appears

## Adding a Dependency

Add an entry to `skills/init/dependencies.json`. Init reads this file and checks/installs each dependency with OS-specific commands.

## Testing

Run `/init` from a clean state to verify the full onboarding flow. The skill is idempotent — rerunning should report all healthy if nothing changed.
