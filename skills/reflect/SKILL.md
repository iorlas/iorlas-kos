---
name: reflect
description: "Captures an observation about what broke, was missing, or emerged during a session. Writes to Knowledge OS Inbox with optional capability hints. Use when completing a task, hitting friction, or when the user says 'reflect', 'observe', or 'capture lesson'."
---

# Reflect — Capture an Observation

You capture what went wrong, what was missing, or what insight emerged during the current session. Observations land in the Knowledge OS Inbox for later triage into capability patches or personal patterns.

**This is NOT a retrospective or interactive session.** Derive the observation, write the file, confirm. Done.

Input: $ARGUMENTS

## Step 1: Derive the Observation

If `$ARGUMENTS` contains text, use it as the raw observation content (voice dump or typed note). Clean it up but preserve the meaning.

If `$ARGUMENTS` is empty, derive from session context by reviewing:
- What capability guidelines were consumed? (deployment platform docs, MCP patterns, etc.)
- What broke, was missing, or required a workaround?
- What insight emerged that wasn't in the guidelines?
- What personal pattern or decision is worth noting?

Synthesize into a specific, actionable observation. Avoid vague statements like "deployment was hard." Instead: "The deployment guideline doesn't mention that `compose.create` requires `environmentId` from the `project.create` response."

**Nothing worth capturing is a valid outcome.** If the session went smoothly — no friction, no missing guidelines, no surprises — say so and stop. Do not force an observation out of a clean session. Minor speed bumps that were resolved in minutes (wrong CLI flag, typo, quick lookup) are not observations. An observation should imply a capability patch or pattern worth recording. If you can't imagine what that patch would be, there's nothing to capture.

```
No observations from this session — the work went smoothly.
```

If nothing to capture, stop here. Do not proceed to Step 2.

## Step 2: Identify Capability Hints

Scan the session for references to capability guidelines or research IDs (e.g., R036 for deployment platform, R020 for MCP patterns). These are hints — best guesses, not authoritative. Leave empty if unclear.

Check `~/Documents/Knowledge/Researches/` folder names for matching IDs if unsure.

The `capability` field is a free-form string array. Any descriptive string is fine: `["R036"]`, `["deployment platform"]`, `["proxy hub", "docker networking"]`. Empty array `[]` is also fine.

## Step 3: Determine Project Context

Same logic as `/inbox`:

Run: `basename "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"`

- `context:` — full cwd path
- `project:` — `"[[{result}]]"` as wiki-link

## Step 4: Write the Observation File

**ID sequence:** scan `~/Documents/Knowledge/Inbox/I????-*.md`, find highest ID, increment. Same sequence as all inbox items.

Create `~/Documents/Knowledge/Inbox/I{NNNN}-{slug}.md`:

```markdown
---
kind: inbox
subtype: observation
id: I{NNNN}
name: "{Brief title — what was observed}"
status: new
created: {YYYY-MM-DDTHH:MM}
context: {full cwd path}
project: "[[{project name}]]"
capability: [{capability hints}]
source: {agent|human}
---

# {Brief title — what was observed}

## What happened

{Concrete description: what broke, what was missing, what the agent had to work around,
or what insight emerged. Be specific — vague observations are useless at triage.}

## Impact

{Why this matters. Omit section if obvious from what-happened.}
```

**Source field:** set to `agent` if the observation was derived from session context (no $ARGUMENTS), `human` if the user provided the content.

**No confirmation needed before writing.** Write immediately, then report.

## Step 5: Confirm and Offer

```
Observation captured: I{NNNN} — {title}
Capability hint: {R036} (or "none identified")

Want to dig into this now, or leave it for triage?
```

If user says "now" — discuss and analyze in the current session.
If user says "triage" or doesn't respond — done.

## What Makes a Good Observation

- **Specific:** "The guideline doesn't mention that `compose.create` requires `environmentId` from the `project.create` response" is good. "Dokploy was hard" is not.
- **Actionable:** A good observation implies a capability patch. If you can't imagine what the patch would be, the observation is too vague.
- **Honest about uncertainty:** If you don't know the root cause, say so. Don't invent one.

## Constraints

- **No git operations.** No add, commit, push.
- **No dedup.** Always create a new file, even if a similar observation exists.
- **No interactive session** unless the user explicitly asks to "dig in."
- **Capability hints are optional.** Empty array is fine. Don't force a match.
