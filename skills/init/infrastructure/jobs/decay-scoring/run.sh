#!/usr/bin/env bash
# Decay Scoring — compute relevance decay for all entities
CADENCE=86400  # 24 hours

KNOWLEDGE_PATH="$HOME/Documents/Knowledge"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

VENV="$KNOWLEDGE_PATH/skills/.venv/bin/python3"
[ -x "$VENV" ] && PY="$VENV" || PY="python3"
"$PY" "$SCRIPT_DIR/decay-scoring.py" --verbose >> "$SCRIPT_DIR/last-run.log" 2>&1

# Auto-commit decay score changes (deterministic, no review needed)
cd "$KNOWLEDGE_PATH" && \
  git add -A -- '*.md' && \
  git diff --cached --quiet || \
  git commit -m "chore: update decay scores (automated)"
