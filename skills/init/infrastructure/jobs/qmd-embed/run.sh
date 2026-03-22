#!/usr/bin/env bash
# QMD Embed — re-index knowledge base for semantic search
CADENCE=1800  # 30 minutes

KNOWLEDGE_PATH="$HOME/Documents/Knowledge"

# Skip if nothing changed since last successful embed
# Uses HEAD SHA + uncommitted .md changes as fingerprint
MARKER="$(dirname "$0")/.last-embed-hash"
CURRENT_HASH="$(cd "$KNOWLEDGE_PATH" && { git rev-parse HEAD; git diff --name-only HEAD -- '*.md'; } | md5sum | cut -d' ' -f1)"
if [ -f "$MARKER" ] && [ "$(cat "$MARKER")" = "$CURRENT_HASH" ]; then
    exit 0
fi

cd "$KNOWLEDGE_PATH" && npx @tobilu/qmd embed 2>&1 || exit 1
echo "$CURRENT_HASH" > "$MARKER"
