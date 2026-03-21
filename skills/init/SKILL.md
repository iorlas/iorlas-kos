---
name: kay-init
description: "Initializes Kay (K) knowledge base: checks dependencies, creates folder structure, sets up QMD semantic search, verifies MCP. Run once before using /kay-inbox or /kay-triage. Use when the user says 'set up kay', 'init kay', 'init k', or when /kay-inbox reports missing folders."
---

# Kay — Init

Set up the personal knowledge base infrastructure. Idempotent — safe to run multiple times.

## Steps

### 1. Detect OS

Detect the current operating system to provide correct install commands:

```bash
uname -s
```

- `Darwin` → macOS (use `brew` commands)
- `Linux` → check for package manager:
  - `which apt` → Debian/Ubuntu (use `apt` commands)
  - `which dnf` → Fedora/RHEL (use `dnf` commands)
  - Otherwise → show `manual` install links

Store the detected platform for use in dependency install suggestions.

### 2. Check dependencies

Read `dependencies.json` (in this skill's directory) and check each dependency:

For each entry, run its `check` command. Report status:

```
Dependencies:
  ✓ node (v22.1.0)
  ✗ qmd — not found
    Install: npm install -g @tobilu/qmd
  ✓ gh (2.45.0) [optional]
```

For missing **required** dependencies: show the install command for the detected OS. Stop here — the user must install required dependencies before proceeding.

For missing **optional** dependencies: show the install command but continue.

### 3. Create folder structure

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
└── Agents/
│   └── Claude/  ← Claude Code native memory (auto-managed)
```

### 4. Set up QMD semantic search

Check if QMD collection `knowledge` exists:
```bash
npx @tobilu/qmd collection list 2>&1
```

If `knowledge` collection is missing, run the `setup` commands from the qmd dependency entry in `dependencies.json`:
```bash
npx @tobilu/qmd collection add ~/Documents/Knowledge --name knowledge
npx @tobilu/qmd context add qmd://knowledge "Personal knowledge base: inbox items (ideas, tasks, notes, reports, processes), projects, people, companies, meeting notes"
npx @tobilu/qmd embed
```

If collection exists but new files need embedding:
```bash
npx @tobilu/qmd embed
```

### 5. Configure Claude Code auto-memory directory

Redirect Claude Code's native memory into Kay so it's git-tracked and durable.

Read `~/.claude/settings.json` and check if `autoMemoryDirectory` is set to `~/Documents/Knowledge/Agents/Claude`.

If missing or different, update `~/.claude/settings.json` directly — add or change the `autoMemoryDirectory` field. Preserve all other settings.

Create the directory if it doesn't exist:
```bash
mkdir -p ~/Documents/Knowledge/Agents/Claude
```

Tell the user to restart Claude Code for the change to take effect.

### 6. Verify MCP servers

For each dependency that has an `mcp` entry in `dependencies.json`, check if the MCP server is registered:

```bash
claude mcp list 2>&1 | grep -i {mcp.name}
```

If missing, add it directly to `~/Documents/Knowledge/.mcp.json`. Read the file, add the server entry, write it back. For QMD:

```json
{
  "mcpServers": {
    "qmd": {
      "command": "npx",
      "args": ["@tobilu/qmd", "mcp"]
    }
  }
}
```

Merge with any existing servers in the file. Tell the user to restart Claude Code for the new MCP server to load.

### 7. Report status

Show a summary:
```
Kay Status:
  Platform:   macOS (brew)
  Deps:       ✓ all required dependencies installed  |  ✗ missing: {list}
  Folders:    ✓ ~/Documents/Knowledge/ (N subdirectories)
  Claude Mem: ✓ autoMemoryDirectory → ~/Documents/Knowledge/Agents/Claude/  |  ✗ not set (fixed above)
  QMD:        ✓ collection 'knowledge' (N files indexed, N embedded)
  MCP:        ✓ qmd server registered  |  ✗ not configured (fixed above)
```
