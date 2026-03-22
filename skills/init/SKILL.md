---
name: kay-init
description: "Initializes Kay (K) knowledge base from scratch or health-checks an existing one. Ontology-driven — reads schema types to generate folder structure. Run once to set up, rerun anytime to heal. Use when the user says 'set up kay', 'init kay', 'init k', or when /inbox reports missing folders."
---

# Kay — Init

Sets up or health-checks the Kay personal knowledge base. Works from zero (fresh install) or on an existing setup (detects drift and fixes it). Ontology-driven — entity schemas define the folder structure.

## Principles

- **Explain before acting.** Before running any check or fix, briefly say what you're about to do and why. This is the front door to Kay — people should feel informed, not surprised.
- **One thing at a time.** Run each check as a separate, readable command. No compound bash chains.
- **Non-technical tone.** Explain *what's wrong*, not commands. But don't hide decisions — if something has consequences, name them.
- **Ask before changing.** Never remove, overwrite, or reconfigure without asking. Use interactive capabilities (ask question, present options) when available, fall back to text.
- **Multiple fixes → plan mode.** If several things need fixing, propose them as a batch first.
- **Cross-platform.** Detect OS and use appropriate paths/commands. Unix: `~/Documents/Knowledge`. Windows: `%USERPROFILE%\Documents\Knowledge`. Venv: Unix uses `bin/python3`, Windows uses `Scripts\python.exe`.

## Step 1: Introduce

Start by telling the user what you're about to do:

> I'll set up your Kay knowledge base — checking dependencies, creating folders from the ontology, configuring search, memory, and background jobs. If anything needs fixing, I'll explain what and ask before making changes.

## Step 2: Check each component

Run each check separately. After each one, briefly report what you found before moving to the next. You must check ALL sections (2.1 through 2.9) — do not stop early even if everything looks healthy so far.

### 2.1 Platform & dependencies
**Why:** Kay needs Node.js, Python, and a few tools.

Read `dependencies.json` from this skill's directory. For each dependency:
- Run its `check` command
- If missing and required → show install command for detected OS. Stop here.
- If missing and optional → show install command, continue.

### 2.2 Kay repository
**Why:** Kay is a git-tracked folder that holds your knowledge.

Check if `~/Documents/Knowledge` exists.

- **Doesn't exist:** create it and initialize git:
  ```
  mkdir -p ~/Documents/Knowledge
  cd ~/Documents/Knowledge && git init
  ```
- **Exists but not a git repo:** ask whether to `git init` (they may have an existing folder).
- **Exists and is a git repo:** healthy.

### 2.3 Ontology-driven folders
**Why:** Each entity type in Kay has its own folder, defined by the ontology.

Read all `.yaml` files in the `ontology/` directory of this skill. Each schema with a `folder` field defines a required directory under `~/Documents/Knowledge/`.

Also ensure these fixed directories exist: `Calls`, `Calls/Assets`, `Assets`, `Agents/Claude`, `Journals`.

Create missing folders silently — this is non-destructive.

### 2.4 Infrastructure
**Why:** Kay has a Python engine (frontmatter parsing, schema validation, entity creation) and background jobs that need to be in the Knowledge repo.

Compare the `infrastructure/` directory bundled with this skill against `~/Documents/Knowledge/internals/core/`:

- **First time (directory missing):** copy the entire `infrastructure/` tree:
  - `infrastructure/engine/` → `~/Documents/Knowledge/internals/core/engine/`
  - `infrastructure/scheduler.py` → `~/Documents/Knowledge/internals/core/scheduler.py`
  - `infrastructure/requirements.txt` → `~/Documents/Knowledge/internals/requirements.txt`
  - `infrastructure/jobs/decay-scoring/` → `~/Documents/Knowledge/internals/core/jobs/decay-scoring/`
  - `infrastructure/jobs/qmd-embed/` → `~/Documents/Knowledge/internals/core/jobs/qmd-embed/`
  - `infrastructure/jobs/ideas-incubation/` → `~/Documents/Knowledge/internals/inbox/jobs/ideas-incubation/`
- **Exists but outdated:** diff key files (scheduler.py, engine/*.py, job run.py scripts). If different, tell the user what changed and ask to update.
- **Current:** skip.

Also copy ontology schemas: `ontology/*.yaml` → corresponding `~/Documents/Knowledge/internals/*/types/` directories. And templates: `templates/` → corresponding `~/Documents/Knowledge/internals/*/templates/`.

### 2.5 Python environment
**Why:** The scheduler and jobs need Python with pyyaml and filelock.

Check if venv exists and has deps:
- Unix: `~/Documents/Knowledge/internals/.venv/bin/python3 -c "import yaml; import filelock"`
- Windows: `~/Documents/Knowledge/internals/.venv/Scripts/python.exe -c "import yaml; import filelock"`

Missing venv → create: `python3 -m venv ~/Documents/Knowledge/internals/.venv`
Missing deps → install: `.venv/bin/pip install -r ~/Documents/Knowledge/internals/requirements.txt`

### 2.6 QMD search index
**Why:** QMD provides semantic search over your knowledge base.
- `npx @tobilu/qmd collection list` — collection `knowledge` must point to `~/Documents/Knowledge` with pattern `**/*.md`
- `npx @tobilu/qmd embed --dry-run` — check if embeddings are current

Missing collection → run setup from `dependencies.json`. Stale embeddings → `npx @tobilu/qmd embed`.

### 2.7 Claude Code memory
**Why:** Memory should write to Kay so it's git-tracked and durable.
- Read `~/.claude/settings.json` — `autoMemoryDirectory` must be `~/Documents/Knowledge/Agents/Claude`
- `find ~/.claude/projects -type d -name "memory"` — check for legacy memory files

Wrong directory → update settings (preserve other fields). Legacy files found → show the user, ask whether to copy into Kay. Never delete originals.

### 2.8 MCP scope
**Why:** QMD's MCP server must be at user scope so it works from any project directory.
- `claude mcp get qmd` — look at the `Scope:` line

Healthy: `User config (available in all your projects)`
Needs fix: `Project config` → `claude mcp add --scope user qmd -- npx @tobilu/qmd mcp`. Ask about removing old project-scope entry.
Not found → `claude mcp add --scope user qmd -- npx @tobilu/qmd mcp`

### 2.9 Status line
**Why:** Kay includes a compact status line: model (O4.6), folder, git branch+dirty, context used (with emoji urgency), cost, code churn.

Check three things:
- Does `~/.claude/hooks/kay-statusline.sh` exist?
- Does `~/.claude/settings.json` have a `statusLine` entry?
- Is the installed script identical to `kay-statusline.sh` bundled with this skill?

**Not installed:** copy from this skill's directory to `~/.claude/hooks/`, make executable, add to settings:
```json
"statusLine": {"type": "command", "command": "bash \"~/.claude/hooks/kay-statusline.sh\""}
```

**Outdated:** default to updating. Only ask if the installed version has custom edits.

**Different (non-Kay) status line:** ask whether to replace.

## Step 3: Scheduler check

Check if `~/Documents/Knowledge/internals/core/scheduler.py` exists and is running: `pgrep -f "scheduler.py"`

- **Running:** report as healthy
- **Not running:** remind the user (see tips below)

## Step 4: Report

```
Kay Status:
  Platform:    {os}
  Deps:        ✓ node, python3, qmd, jq, git, gh  |  ✗ missing: {list}
  Repository:  ✓ git repo  |  ✗ created new  |  ⚠️ not a git repo
  Ontology:    ✓ {N} entity types, {N} folders  |  ✗ folders created
  Infra:       ✓ engine + jobs current  |  ⚠️ updated  |  ✗ installed from scratch
  Python:      ✓ venv ok  |  ✗ created
  QMD:         ✓ {N} files, embeddings ok  |  ✗ collection missing  |  ⚠️ stale
  Memory:      ✓ writing to Kay  |  ✗ configured  |  ⚠️ legacy found
  MCP:         {Scope line from `claude mcp get qmd`}
  Status line: ✓ active (current)  |  ⚠️ outdated  |  ✗ installed
  Scheduler:   ✓ running  |  ✗ not running
```

All green → "Kay is healthy." Fixes applied → list them. Needs input → ask.

Always end with:
> **Tips:**
> - Scheduler: keep `python3 ~/Documents/Knowledge/internals/core/scheduler.py` running in a spare terminal tab
> - Getting started: `cd ~/Documents/Knowledge` and start a session there
> - Add entity types: create a new `.yaml` in the plugin's `ontology/` folder and rerun `/init`
