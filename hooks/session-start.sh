#!/bin/bash
# Kay session-start hook — injects K context + available skills into agent context

SKILLS_INDEX="$HOME/Documents/Knowledge/Skills/INDEX.md"

# Base context
CONTEXT="Kay (K) is the personal knowledge base at ~/Documents/Knowledge.

When the user says \"inbox\", \"capture\", \"save this thought\", or \"put this in K\" — use /inbox to write to Kay, regardless of current working directory.
When the user says \"reflect\" or \"capture lesson\" — use /reflect.
When the user says \"triage\" — use /triage.
When the user says \"create a skill\" or \"improve skill\" — use /skill.

K, Kay, and Knowledge all refer to ~/Documents/Knowledge.
If you need to understand Kay structure, read ~/Documents/Knowledge/CLAUDE.md.
Before creating any Kay entity (research, project, person, etc.), search QMD (vec) for similar existing ones. If score > 0.5, show the match and ask whether to contribute to the existing entity or create new."

# Append K skills if index exists and has entries
if [ -f "$SKILLS_INDEX" ]; then
  # Extract table rows (lines starting with |, excluding header and separator)
  SKILLS=$(grep '^| ' "$SKILLS_INDEX" | grep -v '^| Skill' | grep -v '^|--' | grep -v '<!-- ')
  if [ -n "$SKILLS" ]; then
    CONTEXT="$CONTEXT

K Skills available (read full skill at ~/Documents/Knowledge/Skills/{name}/SKILL.md when relevant):
$SKILLS"
  fi
fi

# Escape for JSON
ESCAPED=$(echo "$CONTEXT" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read())[1:-1])")

echo "{\"hookSpecificOutput\":{\"hookEventName\":\"SessionStart\",\"additionalContext\":\"$ESCAPED\"}}"
