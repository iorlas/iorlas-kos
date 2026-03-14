---
name: init
description: "Initializes the Knowledge OS: creates folder structure, sets up QMD semantic search, verifies MCP. Run once before using /inbox or /triage. Use when the user says 'set up knowledge', 'init knowledge', or when /inbox reports missing folders."
---

# Knowledge OS — Init

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
└── Assets/
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

### 3. Verify QMD MCP server

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

### 4. Report status

Show a summary:
```
Knowledge OS Status:
  Folders:  ✓ ~/Documents/Knowledge/ (N subdirectories)
  QMD:      ✓ collection 'knowledge' (N files indexed, N embedded)
  MCP:      ✓ qmd server registered  |  ✗ run 'claude mcp add ...' (see above)
```
