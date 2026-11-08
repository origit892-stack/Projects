#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

echo "============================================================"
echo "BUNKERGAME DEVELOPMENT POSTFLIGHT"
echo "============================================================"

echo
echo "=== GIT DIFF CHECK ==="
git diff --check -- .

echo
echo "=== CHANGED FILES ==="
git status --short -- . || true

echo
echo "=== FULL-GAME SOURCE ASSERTIONS ==="
python3 tools/workflows/validate_full_game_candidate.py --root .

echo
echo "=== ROJO VALIDATION ==="
"$HOME/.aftman/bin/rojo" sourcemap default.project.json --output sourcemap.json

echo
echo "=== SEMANTIC REVIEW ==="
bds review all

echo
echo "POSTFLIGHT_COMPLETE"
