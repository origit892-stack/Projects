#!/bin/bash
# luau-analyze gate over src/ (syntax + non-strict analysis). Exits non-zero on errors.
set -u
cd "$(dirname "$0")/.." || exit 2
FILES=$(find src -name "*.luau" -o -name "*.lua" | sort)
if [ -z "$FILES" ]; then
  echo "analyze: no luau files yet — skipping (exit 0)"
  exit 0
fi
COUNT=$(printf '%s\n' "$FILES" | wc -l | tr -d ' ')
if luau-analyze --mode=nonstrict $FILES; then
  echo "analyze: OK ($COUNT files)"
else
  RC=$?
  echo "analyze: FAILED ($RC, errors above)"
  exit $RC
fi
