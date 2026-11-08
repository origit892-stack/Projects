#!/bin/zsh

set -u

ROOT="/Users/Ori/Documents/Projects/BunkerGame"
RUNROOT="$ROOT/.opencode/overnight_world_v2"

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$HOME/.aftman/bin:$PATH"

CP="${1:-UNKNOWN}"
STATUS="${2:-INFO}"
shift 2 2>/dev/null || true
MESSAGE="$*"

TS="$(/bin/date '+%Y-%m-%d %H:%M:%S')"
SAFE_CP="$(printf '%s' "$CP" | /usr/bin/tr -cd 'A-Za-z0-9._-')"

printf '%s|%s|%s|%s\n' \
  "$TS" \
  "$SAFE_CP" \
  "$STATUS" \
  "$MESSAGE" \
  >> "$RUNROOT/events.log"

printf '%s\n' "$SAFE_CP" > "$RUNROOT/current_checkpoint.txt"
printf '%s\n' "$MESSAGE" > "$RUNROOT/current_activity.txt"

if [ "$STATUS" = "START" ]; then
  printf '%s\n' "$SAFE_CP" > "$RUNROOT/state.txt"
fi

if [ "$STATUS" = "PASS" ]; then
  printf '%s\n' "$SAFE_CP" > "$RUNROOT/last_passed_checkpoint.txt"

  SNAP="$RUNROOT/checkpoints/${SAFE_CP}_$(/bin/date '+%Y%m%d_%H%M%S')"

  /bin/mkdir -p "$SNAP"

  if [ -d "$ROOT/src" ]; then
    /usr/bin/tar -czf "$SNAP/src.tar.gz" -C "$ROOT" src 2>/dev/null || true
  fi

  if [ -f "$ROOT/default.project.json" ]; then
    /bin/cp "$ROOT/default.project.json" "$SNAP/default.project.json" 2>/dev/null || true
  fi

  if [ -f "$ROOT/opencode.json" ]; then
    /bin/cp "$ROOT/opencode.json" "$SNAP/opencode.json" 2>/dev/null || true
  fi

  if [ -d "$ROOT/src/ServerStorage/GeneratedAssets" ]; then
    /usr/bin/find "$ROOT/src/ServerStorage/GeneratedAssets" \
      -type f \
      -print \
      | /usr/bin/sort \
      > "$SNAP/generated_assets.txt" 2>/dev/null || true
  fi

  /usr/bin/find "$ROOT/src" \
    -type f \
    -print \
    2>/dev/null \
    | /usr/bin/sort \
    > "$SNAP/source_files.txt" || true

  printf '%s\n' "$MESSAGE" > "$SNAP/checkpoint.txt"
  printf '%s\n' "$TS" >> "$SNAP/checkpoint.txt"
fi

printf 'CHECKPOINT|%s|%s|%s\n' "$SAFE_CP" "$STATUS" "$MESSAGE"
