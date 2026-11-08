#!/bin/zsh

ROOT="/Users/Ori/Documents/Projects/BunkerGame"
R="$ROOT/.opencode/overnight_world_v2"

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$HOME/.aftman/bin:$PATH"

printf '%s\n' "Waiting for live run file..."

while true; do
  F="$(/bin/cat "$R/current_run_file.txt" 2>/dev/null)"

  if [ -n "$F" ] && [ -f "$F" ]; then
    printf 'RAW_RUN_FILE=%s\n' "$F"
    exec /usr/bin/tail -n 40 -f "$F"
  fi

  /bin/sleep 2
done
