---
name: init
description: "Initializes Kay (K) knowledge base: creates folder structure, sets up QMD semantic search, verifies MCP. Run once before using /inbox or /triage. Use when the user says 'set up kay', 'init kay', 'init k', or when /inbox reports missing folders."
---

# Kay — Init

Set up the personal knowledge base infrastructure. Idempotent — safe to run multiple times.

## Steps

### 1. Create folder structure

Create these directories if they don't exist:

```
~/Documents/Knowledge/
├── Inbox/
├── Projects/
├── People/
├── Processes/
├── Companies/
├── Researches/
├── References/
├── Calls/
│   └── Assets/
├── Assets/
└── Claude/          ← Claude Code native memory (auto-managed)
```

### 2. Set up QMD semantic search

Check if QMD collection `knowledge` exists:
```bash
npx @tobilu/qmd collection list 2>&1
```

If `knowledge` collection is missing:
```bash
npx @tobilu/qmd collection add ~/Documents/Knowledge --name knowledge
npx @tobilu/qmd context add qmd://knowledge "Personal knowledge base: inbox items (ideas, tasks, notes, reports, processes), projects, people, companies, meeting notes"
npx @tobilu/qmd embed
```

If collection exists but new files need embedding:
```bash
npx @tobilu/qmd embed
```

### 3. Configure Claude Code auto-memory directory

Redirect Claude Code's native memory into Kay so it's git-tracked and durable.

Read `~/.claude/settings.json` and check if `autoMemoryDirectory` is set to `~/Documents/Knowledge/Claude`:

If missing or different, tell the user:
```
Run this in your terminal:
  Open ~/.claude/settings.json and add:
  "autoMemoryDirectory": "~/Documents/Knowledge/Claude"
Then restart Claude Code.
```

Cannot modify settings.json from inside Claude Code — the user must do it manually or via `claude config set`.

Create the directory if it doesn't exist:
```bash
mkdir -p ~/Documents/Knowledge/Claude
```

### 4. Verify QMD MCP server

Check if `qmd` MCP server is registered:
```bash
claude mcp list 2>&1 | grep -i qmd
```

If missing, tell the user to run (cannot run `claude` inside Claude Code):
```
Run this in your terminal:
  claude mcp add --scope user qmd -- npx @tobilu/qmd mcp
Then restart Claude Code.
```

### 5. Report status

Show a summary:
```
Kay Status:
  Folders:    ✓ ~/Documents/Knowledge/ (N subdirectories)
  Claude Mem: ✓ autoMemoryDirectory → ~/Documents/Knowledge/Claude/  |  ✗ set manually (see above)
  QMD:        ✓ collection 'knowledge' (N files indexed, N embedded)
  MCP:        ✓ qmd server registered  |  ✗ run 'claude mcp add ...' (see above)
```
