#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
REPORT_DIR="$ROOT/docs/ai/evidence"
REPORT="$REPORT_DIR/project-inspection-$TIMESTAMP.txt"

mkdir -p "$REPORT_DIR"

{
  echo "============================================================"
  echo "BUNKER DEVELOPMENT SYSTEM"
  echo "PROJECT INSPECTION REPORT"
  echo "============================================================"
  echo "TIMESTAMP: $TIMESTAMP"
  echo "PROJECT: $ROOT"
  echo

  "$ROOT/tools/bds/inventory.sh"

  echo
  echo "=== ROJO SOURCEMAP ==="
  if command -v rojo >/dev/null 2>&1; then
    if rojo sourcemap default.project.json --output sourcemap.json; then
      echo "SOURCEMAP_CREATED: sourcemap.json"
    else
      echo "SOURCEMAP_FAILED"
    fi
  else
    echo "ROJO_NOT_FOUND"
  fi

  echo
  echo "=== PER-FILE INSPECTION ==="

  while IFS= read -r file; do
    echo
    "$ROOT/tools/bds/inspect-file.sh" "$file"
  done < <(
    find src -type f \( -name '*.lua' -o -name '*.luau' \) | sort
  )

  echo
  echo "=== CROSS-PROJECT REQUIRE CALLS ==="
  grep -RIn --include='*.lua' --include='*.luau' 'require(' src || true

  echo
  echo "=== CROSS-PROJECT REMOTES ==="
  grep -RInE \
    --include='*.lua' \
    --include='*.luau' \
    'RemoteEvent|RemoteFunction|OnServerEvent|OnClientEvent|OnServerInvoke|OnClientInvoke|FireClient|FireAllClients|FireServer|InvokeClient|InvokeServer' \
    src || true

  echo
  echo "=== CROSS-PROJECT DATASTORE USAGE ==="
  grep -RInE \
    --include='*.lua' \
    --include='*.luau' \
    'DataStoreService|GetDataStore|GetOrderedDataStore|GetAsync|SetAsync|UpdateAsync|RemoveAsync|IncrementAsync' \
    src || true

  echo
  echo "=== CURRENT GIT DIFF ==="
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git status --short -- .
    git diff --stat -- .
    git diff --check -- . || true
  else
    echo "NOT_A_GIT_REPOSITORY"
  fi
} | tee "$REPORT"

echo
echo "BDS report created:"
echo "  $REPORT"
