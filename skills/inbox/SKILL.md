---
name: inbox
description: "Captures ideas, thoughts, tasks, voice dumps, links, or notes into structured inbox files in ~/Documents/Knowledge/Inbox/. Use when the user says 'capture this', 'save this thought', 'inbox', or dumps raw text/voice transcript to process."
---

# Inbox — Universal Capture

**CAPTURE FIRST, ORGANIZE LATER. Never lose a thought to friction.**

You capture raw input — voice transcripts, pasted links, messy notes, mixed languages — into clean, trackable inbox files with auto-detected types and project context. Split multi-topic dumps into separate files. Clean voice artifacts into readable prose while preserving the user's voice and mixed languages.

Input: $ARGUMENTS

## Unsupported Inputs

- **Audio file path** (`.m4a`, `.mp3`, `.wav`) — say "Audio transcription not yet supported. Please paste the transcript text." and stop.
- **URL only** — say "URL content fetching not yet supported. Capturing the URL as-is." and proceed.

## Output Template

Create `~/Documents/Knowledge/Inbox/I{NNNN}-{slug}.md`:

```markdown
---
kind: inbox
subtype: {idea|task|note|report|reminder}
id: I{NNNN}
name: "{Item Title}"
status: new
created: {YYYY-MM-DDTHH:MM}
context: {full cwd path}
project: "[[{folder name or matched project}]]"
mentions: ["Name1", "Name2"]
source: {voice|text}
---

# {Item Title}

{Cleaned up content}

Source: {if applicable — link, video, person}
```

**ID sequence:** scan `~/Documents/Knowledge/Inbox/I????-*.md`, find highest ID, increment. Start at I0001 if none exist.

**Frontmatter rules:**
- Always include: kind, subtype, id, status, created, context, project, source
- Always include `name` — same as the `# Title` heading
- Include `mentions` only if names found; omit if none
- Include `due_at` only for `subtype: reminder` — ISO format `YYYY-MM-DDTHH:MM`

**Subtype detection:**
- `idea` — concepts, inspirations, hypotheses, "what if" thoughts
- `task` — actionable items, TODOs, things someone needs to do
- `note` — information, observations, references, facts worth recording
- `report` — summaries, status updates, findings, analysis results
- `reminder` — time-triggered notifications ("remind me in 30 mins", "this evening notify me", "by tomorrow 8am")

**Reminder handling:**
When input contains a time expression (relative like "in 30 mins", "tonight", "tomorrow morning" or absolute like "at 19:00", "by 08:00"), detect as `subtype: reminder` and add `due_at:` field in ISO format (`YYYY-MM-DDTHH:MM`). Convert relative times using current time. Fuzzy mappings: "this evening" → 19:00, "tonight" → 21:00, "tomorrow morning" → 09:00.

**After creating the inbox file, create a native macOS Reminder:**
```bash
osascript -e 'set d to (current date) + {N} * minutes' -e 'tell application "Reminders" to make new reminder in list "Reminders" with properties {name:"{name}", due date:d, body:"Knowledge OS: {inbox_id}"}'
```
Convert the user's time expression to minutes from now. Examples: "in 30 mins" → 30, "in 2 hours" → 120, "this evening" → minutes until 19:00, "tonight" → minutes until 21:00, "tomorrow morning" → minutes until next 09:00.

This pushes the notification to Reminders.app which syncs to iPhone/Watch/iPad. No background job needed — the reminder is created at capture time.

**Decision: create inbox file?** For ephemeral reminders ("turn off oven", "take meds") — skip the inbox file, just create the Reminders.app entry. For meaningful reminders ("remind me to write to Alex about the proposal") — create both the inbox file and the Reminders.app entry. Use judgment: if the content has zero knowledge value after firing, skip the file.

## Project Context

Run: `basename "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"`

- `context:` — full cwd path
- `project:` — `"[[{result}]]"` as wiki-link (dangling OK)

If `~/Documents/Knowledge/Projects/{result}.md` exists and a Projects/ file has a matching `git:` remote URL in frontmatter, use that file's name (without .md) as the link target instead.

## Constraints

- **No dedup at capture.** Never skip because "a similar item exists." Dedup is triage, not capture.
- **No git operations.** No add, commit, push. IP protection governs commit timing.
- **No extra fields.** No tags, priority, effort. Those come at triage.
- **Preserve voice.** Keep mixed languages. Don't translate. Don't over-formalize.
- **Mentions = raw strings.** Capture names as plain text. No wiki-links, no entity resolution.
- **Source field:** set to `voice` if input looks like voice transcript, otherwise `text`.

## Example

**Input** (cwd: `/Users/user/Projects/mcp-tools`, git repo, Projects/ file matches remote -> `[[MCP Engineering]]`):
```
so I was watching this David Gaut video about how AI makes you limitless right and it got me thinking about feedback loops. Also we need to figure out MCP security policy for DataArt infosec department Sergei mentioned it again yesterday.
```

**Result:** 2 files created:

`I0004-ai-feedback-loops.md`:
```markdown
---
kind: inbox
subtype: idea
id: I0004
name: "AI feedback loops — from questions to systems"
status: new
created: 2026-03-09T14:30
context: /Users/user/Projects/mcp-tools
project: "[[MCP Engineering]]"
source: voice
---

# AI feedback loops — from questions to systems

Feedback loops in AI usage. Higher order loops: asking AI simple questions -> asking AI how to approach questions -> building systems that track and cross-link questions.

Source: David Gaut YouTube video about AI making you limitless
```

`I0005-mcp-security-policy.md` — subtype: task, mentions: ["Sergei"]

Summary shown to user.
```
