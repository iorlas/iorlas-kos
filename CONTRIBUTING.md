# Contributing to Kay

## Development Setup

Kay skills are Claude Code plugins. To develop locally with instant feedback:

### 1. Install Kay from the marketplace

```bash
claude plugin marketplace add https://github.com/iorlas/iorlas-marketplace.git
claude plugin install iorlas-kay@iorlas-marketplace
```

### 2. Symlink your workspace over the cached install

The marketplace install clones a snapshot into `~/.claude/plugins/cache/`. Replace it with a symlink to your local clone so edits are picked up immediately:

```bash
git clone https://github.com/iorlas/iorlas-kay.git
CACHE_DIR=$(find ~/.claude/plugins/cache -type d -name "iorlas-kay" | head -1)
VERSION=$(ls "$CACHE_DIR" | head -1)
rm -rf "$CACHE_DIR/$VERSION"
ln -s "$(pwd)/iorlas-kay" "$CACHE_DIR/$VERSION"
```

### 3. Edit and reload

Edit any file in `skills/`, `hooks/`, or `.claude-plugin/`. Then inside Claude Code:

```
/reload-plugins
```

Changes are picked up instantly. No reinstall, no restart, no push needed.

### 4. When done

Push your changes. Others (or your future self) can pick them up with:

```bash
claude plugin update iorlas-kay@iorlas-marketplace
```

This overwrites the symlink with a fresh clone from GitHub — back to "installed" mode.

## Project Structure

```
iorlas-kay/
  .claude-plugin/plugin.json   -- plugin metadata
  hooks/hooks.json              -- SessionStart hook (announces Kay to every session)
  skills/
    init/
      SKILL.md                  -- /kay-init: full setup wizard
      dependencies.json         -- dependency registry (node, qmd, gh, ...)
    inbox/SKILL.md              -- /inbox: universal capture
    reflect/SKILL.md            -- /reflect: observation capture
    triage/SKILL.md             -- /triage: inbox processing
    consolidate/SKILL.md        -- /consolidate: entity merge
```

## Adding a Dependency

Add an entry to `skills/init/dependencies.json`. The `/kay-init` skill reads this file and checks/installs each dependency with OS-specific commands.

## Skill Naming

- Most skills use short names: `inbox`, `reflect`, `triage`, `consolidate`
- Only `kay-init` is prefixed — to avoid clashing with the built-in `/init` command
