#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

TASK_FILE="docs/director/CURRENT-TASK.md"

echo "============================================================"
echo "BUNKERGAME CURRENT TASK VALIDATION"
echo "============================================================"
echo

if [ ! -f "$TASK_FILE" ]; then
    echo "ERROR: Missing $TASK_FILE"
    exit 1
fi

echo "=== ACTIVE TASK ==="
TASK_ID="$(awk '
    /^## ID[[:space:]]*$/ {
        getline
        while ($0 ~ /^[[:space:]]*$/) getline
        print
        exit
    }
' "$TASK_FILE")"

if [ -z "$TASK_ID" ]; then
    TASK_ID="UNKNOWN"
fi

echo "$TASK_ID"
echo

echo "=== PREFLIGHT ==="
tools/workflows/preflight.sh

echo
echo "=== BDS INSPECT ==="
bds inspect

echo
echo "=== DETECT LUA/LUAU FILES TO VALIDATE ==="

FILES=()

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    while IFS= read -r file; do
        [ -n "$file" ] || continue
        [ -f "$file" ] || continue

        case "$file" in
            *.lua|*.luau)
                FILES+=("$file")
                ;;
        esac
    done < <(
        {
            git diff --name-only --diff-filter=ACMR
            git diff --cached --name-only --diff-filter=ACMR
            git ls-files --others --exclude-standard
        } | sort -u
    )
fi

if [ "${#FILES[@]}" -eq 0 ]; then
    echo "No changed/untracked Lua or Luau files detected."
else
    printf '%s\n' "${FILES[@]}"
fi

echo
echo "=== AST VALIDATION ==="

AST_FAILED=0

if [ "${#FILES[@]}" -eq 0 ]; then
    echo "SKIP: no Lua/Luau files require AST validation."
else
    for file in "${FILES[@]}"; do
        echo
        echo "--- $file ---"

        if ! bds ast "$file"; then
            echo "AST_FAIL: $file"
            AST_FAILED=1
        fi
    done
fi

if [ "$AST_FAILED" -ne 0 ]; then
    echo
    echo "ERROR: AST validation failed."
    exit 1
fi

echo
echo "=== BDS REVIEW: PROJECT ==="
bds review project

echo
echo "=== BDS REVIEW: ALL ==="
bds review all

echo
echo "=== POSTFLIGHT ==="
tools/workflows/postflight.sh

echo
echo "============================================================"
echo "CURRENT TASK VALIDATION COMPLETE"
echo "TASK: $TASK_ID"
echo "============================================================"
