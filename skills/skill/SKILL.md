---
name: skill
description: "Use when the user wants to create a new K skill or improve an existing one. Triggers: 'create a skill for X', 'improve the deployment skill', 'make a skill out of this', or when triage identifies observations that should become or improve a skill."
---

# Skill — Create or Improve K Skills

You create new skills or improve existing ones in `~/Documents/Knowledge/Skills/`. A skill is reusable knowledge that agents discover and follow across projects.

Input: $ARGUMENTS

## Step 1: Determine Intent

If `$ARGUMENTS` names an existing skill from `~/Documents/Knowledge/Skills/INDEX.md` → **Improve** flow.
If `$ARGUMENTS` describes something new → **Create** flow.
If ambiguous, check INDEX.md and ask.

---

## Create Flow

### 1a. Research K

Search the knowledge base for related material:

- **QMD search** (lex + vec) for the topic across all collections
- **Inbox items** — grep `~/Documents/Knowledge/Inbox/` for related observations, ideas, notes
- **Researches** — check `~/Documents/Knowledge/Researches/` for existing research on the topic
- **Projects** — check `~/Documents/Knowledge/Projects/` for projects that encountered this problem

Present findings to the user:
```
Found related material:
- R036 (Deployment Platform) — has guidelines for compose deployment
- I0042 [observation]: Deploy requires environmentId
- I0043 [observation]: Traefik labels undocumented
- 2 inbox ideas related to deployment automation

Should I synthesize these into the skill, or start fresh?
```

### 1b. Research the Domain

If the topic involves external tools, APIs, or practices the knowledge base doesn't fully cover:

- Search the web for current best practices
- Read relevant documentation
- Understand the state of the art

This ensures the skill isn't just recycled pain — it incorporates known solutions.

### 1c. Write the Skill

Create `~/Documents/Knowledge/Skills/{name}/SKILL.md`:

```markdown
---
name: {skill-name}
description: "Use when {specific triggering conditions}. {What problem this solves.}"
---

# {Skill Title}

{What this skill helps you do. Core principle in 1-2 sentences.}

## When to Use

{Bullet list of situations, symptoms, triggers.}

## When NOT to Use

{What this skill is not for — prevents misapplication.}

## How

{The actual knowledge — steps, patterns, decisions, gotchas.
Be specific and actionable. Avoid vague advice.
Include concrete examples where they help.}

## Common Mistakes

{What goes wrong and how to avoid it. Omit if nothing non-obvious.}
```

**Naming rules:**
- Directory name: lowercase, hyphens, descriptive (`deployment`, `diagram-generation`, `slide-decks`)
- `name` field: same as directory name
- `description`: starts with "Use when...", describes triggering conditions only, not the workflow

**Quality principles (borrowed from superpowers CSO):**
- Description tells agents WHEN to use, not WHAT it does
- Use concrete triggers and symptoms in the description
- Keep it concise — every token competes with conversation context
- One excellent example beats many mediocre ones

### 1d. Update the Index

Add a row to `~/Documents/Knowledge/Skills/INDEX.md`:

```markdown
| {name} | {one-line description} | {what it's NOT for} |
```

### 1e. Confirm

```
Skill created: Skills/{name}/SKILL.md
Added to INDEX.md

The skill is now discoverable in all sessions.
```

---

## Improve Flow

### 2a. Read Current State

Read the existing skill at `~/Documents/Knowledge/Skills/{name}/SKILL.md`.

### 2b. Gather Improvement Context

Depending on what triggered the improvement:

**If called from triage** (observations routed to this skill):
- Read the observation(s) that triggered the improvement
- Understand what friction occurred and what workaround was used

**If called by user** ("improve the deployment skill"):
- Ask what's wrong or what's missing
- Search K for recent observations, inbox items, or session context related to this skill

**If called after using the skill** ("that skill didn't work well"):
- Review current session context for what went wrong
- Identify the gap between what the skill says and what was actually needed

### 2c. Research if Needed

If the improvement involves new tools, APIs, or practices — do the research. Don't just patch from pain; incorporate the right solution.

### 2d. Apply Improvements

Edit the SKILL.md:
- Add missing steps or gotchas discovered from observations
- Clarify confusing sections that caused friction
- Remove advice that turned out to be wrong
- Update examples if they no longer reflect best practice

**Don't bloat.** Each improvement should make the skill more precise, not longer. If adding a section, consider whether an existing section should be tightened.

### 2e. Update Index if Description Changed

If the skill's scope or description changed, update the INDEX.md row.

### 2f. Confirm

```
Skill improved: Skills/{name}/SKILL.md
Changes: {brief summary of what changed and why}
```

---

## Constraints

- **Always search K first.** Never create a skill from thin air when related material exists.
- **No git operations.** No add, commit, push.
- **Skills are agent-agnostic.** Write plain markdown that any AI agent can follow — no Claude-specific tool names, no plugin references.
- **No draft/mature distinction.** A skill is a skill. Quality shows in the content.
- **Don't duplicate existing K skills.** Check INDEX.md before creating. If a related skill exists, improve it instead.
- **Keep descriptions trigger-focused.** "Use when..." — never summarize the workflow in the description.
