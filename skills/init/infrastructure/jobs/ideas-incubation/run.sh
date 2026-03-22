#!/usr/bin/env bash
# Ideas Incubation — headless Claude researches new inbox ideas
CADENCE=1800  # 30 minutes

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
KNOWLEDGE_PATH="$HOME/Documents/Knowledge"
VENV="$KNOWLEDGE_PATH/skills/.venv/bin/python3"
[ -x "$VENV" ] && PY="$VENV" || PY="python3"
"$PY" "$SCRIPT_DIR/run.py" --verbose
