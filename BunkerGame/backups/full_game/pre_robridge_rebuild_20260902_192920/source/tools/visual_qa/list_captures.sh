#!/bin/bash
set -eu

ROOT="/Users/Ori/Documents/Projects/BunkerGame"
DIR="$ROOT/visual-qa/captures"

mkdir -p "$DIR"

echo "=== BUNKERGAME VISUAL QA CAPTURES ==="
find "$DIR" -type f -name '*.mp4' -print0 |
    xargs -0 ls -lht 2>/dev/null || true
