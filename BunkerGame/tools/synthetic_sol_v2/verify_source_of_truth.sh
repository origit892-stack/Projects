#!/bin/bash
set -e

ROOT="/Users/Ori/Documents/Projects/BunkerGame"
cd "$ROOT"

ROJO="/Users/Ori/.aftman/bin/rojo"

if [ ! -x "$ROJO" ]; then
  echo "ROJO_SOURCE_OF_TRUTH=FAIL"
  echo "Missing canonical Rojo: $ROJO"
  exit 1
fi

SOURCE="src/Workspace/SyntheticSolApproach.model.json"

if [ ! -f "$SOURCE" ]; then
  echo "ROJO_SOURCE_OF_TRUTH=FAIL"
  echo "Missing canonical source: $SOURCE"
  exit 1
fi

echo "SOURCE_PRESENT=YES"
echo "SOURCE_BYTES=$(wc -c < "$SOURCE" | tr -d ' ')"

python3 - <<'PY'
import json
from pathlib import Path

p = Path("src/Workspace/SyntheticSolApproach.model.json")

try:
    data = json.loads(p.read_text())
except Exception as e:
    print("SOURCE_JSON_VALID=NO")
    print("ERROR=" + str(e))
    raise SystemExit(1)

print("SOURCE_JSON_VALID=YES")

def count_nodes(x):
    if isinstance(x, dict):
        return 1 + sum(count_nodes(v) for v in x.values())
    if isinstance(x, list):
        return sum(count_nodes(v) for v in x)
    return 0

print("SOURCE_STRUCTURAL_NODE_COUNT=" + str(count_nodes(data)))
PY

"$ROJO" sourcemap default.project.json \
  --output /tmp/synthetic-sol-v2-sourcemap.json

echo "ROJO_SOURCEMAP=PASS"

"$ROJO" build default.project.json \
  --output /tmp/synthetic-sol-v2-build.rbxlx

echo "ROJO_BUILD=PASS"

if [ ! -s /tmp/synthetic-sol-v2-build.rbxlx ]; then
  echo "ROJO_SOURCE_OF_TRUTH=FAIL"
  echo "Rojo build artifact empty"
  exit 1
fi

echo "ROJO_BUILD_BYTES=$(wc -c < /tmp/synthetic-sol-v2-build.rbxlx | tr -d ' ')"

echo
echo "STATIC_SOURCE_GATE=PASS"
echo
echo "NOTE:"
echo "Studio double-sync verification is still required before:"
echo "ROJO_SOURCE_OF_TRUTH=PASS"
