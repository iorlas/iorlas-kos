---
name: reflect
description: "Emit an evolution signal — record what happened, what broke, what's needed. Writes OCEL-formatted signals to Evolution/signals/. Use mid-task on friction, at task completion, or when the user says 'reflect'."
---

# Reflect — Emit Evolution Signal

Record what happened. Write a signal file to `~/Documents/Knowledge/Evolution/signals/`. Done.

**This is a write operation, not a discussion.** Derive the signal, write the file, confirm. No interactive session unless explicitly asked.

Input: $ARGUMENTS

## Step 1: Derive the Signal

Determine the signal type and content from one of these sources:

**If `$ARGUMENTS` contains text:** Use it as raw content. Clean up but preserve meaning. Infer the signal type from content.

**If `$ARGUMENTS` is empty:** Derive from session context:
- What friction was encountered? What broke or was missing?
- What skills were used? What skills should have existed but didn't?
- What decisions were made? What needs emerged?
- What worked well that should be preserved?

**Signal types** — pick one:
- `problem` — something broke, was unclear, or caused friction
- `need` — "I wish X existed", desire for a skill/capability that doesn't exist
- `usage` — skill was invoked (even if it worked fine)
- `limitation` — skill exists but doesn't cover this use case
- `decision` — a final decision was made, with rationale
- `resolution` — a problem was solved, with method

**Nothing worth capturing is valid.** If the session went smoothly — no friction, no missing skills, no surprises — say so and stop. Do not force a signal. Minor speed bumps resolved in seconds are not signals.

If nothing to capture, stop here.

## Step 2: Gather Context Automatically

Collect these from the current session — do not ask the user:

```bash
# Current working directory
pwd

# Project name (from git or directory)
basename "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
```

**Skills in context:** List ALL skills that were loaded or invoked during this session. For each, note whether it was actually invoked (`true`) or just available (`false`). Check the system-reminder at conversation start for the skills list.

**Session ID:** Use the first 8 characters of a hash of the current timestamp + cwd, or any unique session identifier available.

**Target skill:** If this signal is about a specific existing skill, name it. If it's about a new activity with no skill → leave empty.

## Step 3: Write the Signal File

**Naming:** `{YYYY-MM-DD}-{HHmm}-{slug}.yaml`

**Location:** `~/Documents/Knowledge/Evolution/signals/`

Create the directory if it doesn't exist: `mkdir -p ~/Documents/Knowledge/Evolution/signals`

```yaml
---
type: signal
subtype: {problem|need|usage|limitation|decision|resolution}
timestamp: {ISO 8601}
session_id: {unique session identifier}

context:
  cwd: {full cwd path}
  project: {project name}
  skills_in_context:
    - name: {skill name}
      invoked: {true|false}
    # ... all skills loaded this session

target_skill: {skill name, or omit if no skill applies}

expected: "{what was supposed to happen — omit if not applicable}"
actual: "{what actually happened — omit if not applicable}"
---

{Free-text narrative. Be specific and concrete. Include what was tried,
why it failed, what workaround was used, what the agent wished existed.
Rich context here helps the evolution engine make better skill changes.}
```

**Field rules:**
- `expected`/`actual` — required for `problem` and `limitation` signals. Optional for others.
- `target_skill` — omit entirely when no existing skill is relevant (e.g., "wrote a poem for the first time").
- `skills_in_context` — always populated. Even "no skills were loaded" is useful information.
- `context.cwd` and `context.project` — always populated.

## Step 4: Commit

```bash
cd ~/Documents/Knowledge && git add Evolution/signals/ && git commit -m "signal: {slug}"
```

## Step 5: Confirm

```
Signal emitted: {filename}
Type: {subtype} | Target: {skill or "none"} | Project: {project}
```

One line. Done.

## Constraints

- **No Inbox writes.** Signals go to `Evolution/signals/`, never to `Inbox/`.
- **No dedup.** Always create a new signal file.
- **No interactive session** unless the user explicitly asks to discuss.
- **Lightweight.** This should take <30 seconds including the commit.
- **Auto-create directory.** If `Evolution/signals/` doesn't exist, create it.
