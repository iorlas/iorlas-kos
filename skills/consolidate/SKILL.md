---
name: kay-consolidate
description: "Discovers clusters of related Kay entities, proposes merges, and executes consolidation. Use when the user says 'consolidate', 'find clusters', 'merge researches', or during periodic knowledge maintenance."
---

# Consolidate — Discover, Propose, Merge

Find scattered Kay entities that belong together and consolidate them into living guides.

Input: $ARGUMENTS

## Modes

Parse `$ARGUMENTS` to determine mode:

- **No arguments or "discover"** → Discovery mode
- **"propose {cluster}"** → Propose mode for a specific cluster
- **"merge {sources} --into {target}"** → Execute mode
- **"status"** → Show known clusters and their state
- **"sync"** or **"sync {entity}"** → Check project↔research alignment

---

## Mode 1: Discover

Find natural clusters of related entities. Two signals combined:

### Signal A: Cross-reference graph

Scan all `~/Documents/Knowledge/Researches/*/README.md` and `~/Documents/Knowledge/Projects/*/README.md` for cross-references:

```
Patterns to match:
  R0[0-9][0-9]  or  R[0-9]{3}     — research IDs in text
  [[NNN-slug]]                      — wikilinks
  ../NNN-slug/                      — relative links
```

Build adjacency: which entity references which. Identify dense subgraphs (3+ entities with 3+ mutual references).

### Signal B: Semantic similarity (QMD)

For each entity updated in the last 30 days:
1. Take its `name` field from frontmatter
2. Run QMD `vec` search against all entities
3. Matches with score > 0.5 that aren't already in a cross-reference cluster = **hidden cluster candidates**

### Output

```
Clusters found: N

Cluster 1: [Topic Name]
  Members: R007, R019, R026, R046
  Hub: R007 (most referenced)
  Internal refs: 12
  Recommendation: MERGE — high overlap, same domain

Cluster 2: [Topic Name]
  Members: R031, R037, R039
  Hub: R037
  Internal refs: 8
  Recommendation: MOC — related but distinct scopes

Hidden similarities (no cross-references, but semantically close):
  R073 ↔ R074 (score: 0.62) — consider linking

Run /consolidate propose "Cluster 1" to see merge details.
```

### Cluster recommendations

- **MERGE** — 4+ mutual references, overlapping scope, same domain. Consolidation candidate.
- **MOC** — 3+ references but distinct scopes. Create a Map of Content linking them, don't merge.
- **LINK** — 2 entities with semantic similarity but no cross-references. Just add cross-references.

---

## Mode 2: Propose

Show the merge plan for a specific cluster before executing.

Input: cluster name or member IDs (e.g., "propose AI Engineering" or "propose R007 R019 R026 R046")

### Steps

1. Read all member READMEs fully
2. Identify the **hub** (most referenced, most complete) — this becomes the merge target
3. For each non-hub member, identify:
   - **Unique content** — prescriptive material not in the hub (will be absorbed)
   - **Redundant content** — already covered by the hub (will be dropped)
   - **Conflicting content** — contradicts the hub (will be flagged for human decision)
4. Check what references each member externally (outside the cluster) — these must not break

### Output

```
Merge Plan: AI Engineering & Adoption

Target: R007 (Agentic SDLC Best Practices) — promoted to consolidated guide
  Current size: ~200 lines

Absorb from R019 (AI Engineering Guidelines):
  + Meta-framework for composable guidelines (unique)
  + Instruction effectiveness data: Vercel 100% vs 53% (unique)
  ~ Guideline format recommendations (overlaps R007 section 3 — merge)

Absorb from R026 (AI Adoption Audit):
  + Maturity model (Levels 0-4) (unique)
  + Self-assessment form template (unique)
  + BevNET audit report template (unique)
  ~ 3-stage adoption model (already in R007 — deduplicate)

Absorb from R046 (AI Adoption Dev Skill):
  + 8-module training curriculum (unique)
  + Module-to-maturity mapping (unique)
  ~ R007/R026 references (will become internal sections)

After merge:
  R019 → redirect stub in _consolidated/, consolidated_into: R007
  R026 → redirect stub in _consolidated/, consolidated_into: R007
  R046 → redirect stub in _consolidated/, consolidated_into: R007

External references that will be updated:
  Projects/051-ai-lab-consulting/readme.md mentions R026, R007, R019
  Researches/028-projects-estimation/... mentions R026, R007
  (These wikilinks still resolve — stubs have the ID)

Conflicts to resolve:
  None detected.

Run /consolidate merge R019 R026 R046 --into R007 to execute.
```

---

## Mode 3: Merge (Execute)

Input: `merge R019 R026 R046 --into R007`

### Steps

1. **Absorb content into target.**
   - Read each source entity fully
   - Extract unique prescriptive content (guidelines, templates, models, checklists)
   - Add to the target README as new sections or subsections
   - Preserve source attribution: `<!-- Absorbed from R019 (AI Engineering Guidelines) -->`
   - If the target's README grows too large, split into sub-files within the target's directory

2. **Create redirect stubs.**
   - For each source entity, replace its README.md with a redirect stub:

```markdown
---
kind: research
id: '{original_id}'
name: '{original_name}'
status: consolidated
consolidated_into: '[[{target_id}-{target_slug}]]'
consolidated_at: {YYYY-MM-DD}
original_created: {original_created_date}
---

# {original_name}

This research has been consolidated into [[{target_id}-{target_slug}]].

All prescriptive content has been absorbed. This stub preserves the entity ID
for cross-reference integrity.
```

3. **Move source directories to archive.**

```bash
mkdir -p ~/Documents/Knowledge/Researches/_consolidated/
mv ~/Documents/Knowledge/Researches/{source_id}-{slug}/ \
   ~/Documents/Knowledge/Researches/_consolidated/
```

4. **Update target frontmatter.**
   - Add `sources:` field listing absorbed entity IDs
   - Bump `updated:` date

5. **Report.**

```
Consolidation complete.

Target: R007 (Agentic SDLC Best Practices)
  Absorbed: R019, R026, R046
  New sections added: 4
  Target size: ~200 → ~450 lines

Stubs created:
  _consolidated/019-ai-engineering-guidelines/README.md
  _consolidated/026-ai-adoption-audit/README.md
  _consolidated/046-ai-adoption-dev-skill/README.md

Cross-references preserved: all wikilinks to R019/R026/R046 still resolve.
No git operations performed — commit when ready.
```

---

## Mode 4: Status

Show current state of all known clusters.

```
Kay Consolidation Status

Active clusters:
  AI Engineering (R007 hub) — 4 members, MERGE recommended, not yet merged
  YouTube Content (R037 hub) — 8 members, 4 MERGE + 4 MOC

Completed merges:
  (none yet)

_consolidated/ archive:
  (empty)

Stale entities (no references, no updates in 90 days):
  R018 — Content Readability Optimization (empty skeleton)
  R027 — Claudebox Strategy (empty template)
```

---

## Mode 5: Sync

Check alignment between projects and the researches they depend on. Two directions:

Input: `sync` (all projects) or `sync P051` (one project)

### Propagation (Research → Project)

When a research updates, projects referencing it may be stale.

**Detection:**
1. Scan project README frontmatter for `depends:` or body text for research wikilinks (`[[NNN-slug]]`, `R0NN`)
2. Compare research `updated` date vs project `updated` date
3. If research is newer → project is stale for that dependency

### Harvesting (Project → Research)

When a project produces lessons, they should route to the right research.

**Detection:**
1. Scan Inbox for items where `project` matches this project AND (`capability` hints match a research OR `subtype: observation`)
2. Items with `status: new` = unrouted lessons
3. Flag them for routing to the referenced research

### Output

```
Sync: Project 051 (AI Lab Consulting)

STALE dependencies (research updated after project):
  R007 (Agentic SDLC) — research: 2026-03-19, project: 2026-03-15
    Changes: absorbed R019, R026, R046 (consolidation)
    → Review new sections in R007 and update project references

  R036 (Deployment Platform) — OK (both 2026-03-17)

Unrouted lessons from this project:
  I0071 — "maturity model missing Level 2.5" (observation, status: new)
    capability hint: R007
    → Route to R007? [triage decides]

  I0073 — "workshop timing too tight for M3 module" (observation, status: new)
    capability hint: R046
    → R046 is consolidated into R007. Route to R007.

No action needed for R036.
```

### Sync during triage

When `/triage` processes an entity, it can call sync silently:

- Entity is a **research that was just updated** → check which projects depend on it, flag stale ones
- Entity is a **project with new observations** → check if observations should route to a research
- Entity is a **consolidated stub** → redirect any new references to the merge target

This is automatic — no separate `/consolidate sync` needed during triage. The standalone `sync` command is for on-demand checks outside triage.

### Handling consolidated entities

When sync finds a project referencing a consolidated stub (e.g., R026 which is now `consolidated_into: R007`):

```
Reference update needed:
  Project 051 references R026 (AI Adoption Audit)
  R026 was consolidated into R007 (Agentic SDLC) on 2026-03-19
  → Update project reference from R026 to R007?
```

This catches stale references that point to archived entities.

---

## Constraints

- **No git operations.** No add, commit, push. User commits when ready.
- **Never delete source content.** Always move to `_consolidated/`, never `rm`.
- **Preserve all cross-references.** Redirect stubs keep the entity ID alive.
- **Human decides what to merge.** Discovery and proposals are automatic. Execution requires explicit `/consolidate merge` command.
- **Conflicts require human input.** If two sources contradict each other, flag it and ask — don't silently pick one.
- **Sub-files of source entities** (analysis.md, sources.md, etc.) move with the directory to `_consolidated/`. They're preserved but archived.
