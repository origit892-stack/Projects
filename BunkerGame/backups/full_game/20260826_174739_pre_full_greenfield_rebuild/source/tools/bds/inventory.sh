#!/bin/bash
set -euo pipefail

echo "============================================================"
echo "BDS PROJECT INVENTORY"
echo "============================================================"
echo

echo "=== PROJECT ROOT ==="
pwd
echo

echo "=== GIT STATUS ==="
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git status --short
else
  echo "NOT_A_GIT_REPOSITORY"
fi
echo

echo "=== ROJO PROJECT FILES ==="
find . -type f -name '*.project.json' -not -path './.git/*' | sort
echo

echo "=== LUA AND LUAU FILES ==="
find src -type f \( -name '*.lua' -o -name '*.luau' \) | sort
echo

echo "=== ROBLOX MODEL FILES ==="
find src -type f \( \
  -name '*.rbxm' -o \
  -name '*.rbxmx' -o \
  -name '*.rbxl' -o \
  -name '*.rbxlx' \
\) | sort
echo

echo "=== SOURCE LINE COUNTS ==="
find src -type f \( -name '*.lua' -o -name '*.luau' \) -print0 |
  xargs -0 wc -l |
  sort -n
