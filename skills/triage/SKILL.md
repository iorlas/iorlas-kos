---
name: triage
description: "Processes inbox items: reviews new captures, resolves mentions to entities, links projects, updates status. Handles observations with capability routing. Use when the user says 'triage inbox', 'process inbox', or 'review captures'."
---

# Inbox Triage

Process `status: new` items in `~/Documents/Knowledge/Inbox/`. For each item: review, resolve mentions, link entities, update status. Observations get special handling — routed to capability patches or personal patterns.

Input: $ARGUMENTS

## Process

### 1. Stats header

Before processing, show a breakdown of what's pending:

```bash
grep -rl 'status: new' ~/Documents/Knowledge/Inbox/I????-*.md
```

Read each file's frontmatter and group by subtype. Display:

```
Inbox items pending triage: N
  observations: X
    deployment platform: Y
    MCP patterns: Z
    no capability tagged: W
  ideas: A
  tasks: B
  notes: C
```

If `$ARGUMENTS` contains `capability:{hint}` (e.g., `capability:R036` or `capability:deployment platform`), filter to only show observations matching that capability hint. Tell the user you're filtering.

If `$ARGUMENTS` specifies an ID (e.g., `I0005`), process only that item. Otherwise process all `status: new` items.

### 2. For each standard item (subtype: idea, task, note, report)

Read the file and:

**a. Resolve mentions** — match raw mention strings against existing entity files:
- Check `~/Documents/Knowledge/People/*/README.md` and `~/Documents/Knowledge/Companies/*/README.md`
- If a match exists, convert the mention to a wiki-link in the body text: `[[Person Name]]`
- If no match, ask the user: "Create entity for {name}? (Person/Company/Skip)"
- If user says create: make a stub entity file with minimal frontmatter

**b. Verify project link** — if `project` field is empty or generic:
- Check if content hints at a specific project
- Check `~/Documents/Knowledge/Projects/` for matches
- Ask user to confirm or skip

**c. Review subtype** — show the item to the user with detected subtype. Ask: "Correct? (y/change/skip)"

**d. Update status** — change `status: new` to `status: triaged` in frontmatter. Set `updated:` to today's date.

### 3. For each observation (subtype: observation)

Read the file and:

**a. Show the observation** — display title + "What happened" section to the user.

**b. Assess root cause** — the `capability:` field is a hint only. Determine with the user:
- Is this really about the tagged capability?
- Is it about a different capability?
- Is it a personal pattern (user's decision-making, not a guideline gap)?
- Is it noise (too project-specific to generalize)?

**c. Propose routing** — one of:
- **Capability patch** → summarize what should change in the capability guideline. Identify which file in the Researches/ folder should be updated and what the patch should say. Ask user to approve or edit. If approved, apply the patch.
- **Personal pattern** → note it for `~/Documents/Knowledge/People/056-denis-tomilin/collaboration_patterns.md` or `ai_corrections.md`. Ask user to confirm.
- **Discard** → too specific, one-off, not reusable. Explain why.

**d. Update status** — change `status: new` to `status: triaged` in frontmatter. Set `updated:` to today's date.

### 4. Re-embed

After processing all items:
```bash
npx @tobilu/qmd embed
```

### 5. Summary

```
Triaged N item(s):
- I0042 [observation]: Deploy requires environmentId → capability patch applied to R036
- I0043 [idea]: AI feedback loops → triaged, project: [[Knowledge]]
- I0044 [task]: MCP security doc → triaged, entity created: [[Sergei]]
```

## Constraints

- **Always ask before creating entities.** Never auto-create People or Company files.
- **Don't change item content.** Only update frontmatter, convert mentions to wiki-links, and (for observations) apply approved capability patches to external files.
- **Don't delete or merge items.** Dedup is a separate decision the user makes.
- **No git operations.** IP protection governs commit timing.
- **One item at a time.** Show each item, get confirmation, move on. Don't batch silently.
- **Observations need human judgment.** Never auto-apply capability patches. Always propose and wait for approval.
