#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

echo "============================================================"
echo "BUNKERGAME DEVELOPMENT PREFLIGHT"
echo "============================================================"

echo
echo "=== BDS DOCTOR ==="
bds doctor

echo
echo "=== GIT STATUS ==="
git status --short -- . || true

echo
echo "=== ROJO SOURCEMAP ==="
"$HOME/.aftman/bin/rojo" sourcemap default.project.json --output sourcemap.json

echo
echo "=== PROJECT REVIEW ==="
bds review project

echo
echo "=== COMPLETE REVIEW ==="
bds review all

echo
echo "PREFLIGHT_COMPLETE"
