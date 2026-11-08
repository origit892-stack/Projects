#!/bin/bash
cd /Users/Ori/Documents/Projects/BunkerGame || exit 1
LOG="artifacts/overnight_aaa_watchdog.log"
NOHUP="artifacts/overnight_aaa_watchdog.nohup.log"
STATE="artifacts/overnight_aaa_watchdog_state.json"
while true; do
  clear
  NOW=$(date +%s)
  LAST_CHECK=$(grep 'WATCHDOG_CHECK' "$LOG" 2>/dev/null | tail -1 | cut -c1-19)
  if [ -n "$LAST_CHECK" ]; then
    LAST_EPOCH=$(date -j -f '%Y-%m-%d %H:%M:%S' "$LAST_CHECK" '+%s' 2>/dev/null || echo "$NOW")
    ELAPSED=$((NOW-LAST_EPOCH))
    REMAIN=$((300-ELAPSED))
    [ "$REMAIN" -lt 0 ] && REMAIN=0
  else
    REMAIN=0
  fi
  MM=$((REMAIN/60)); SS=$((REMAIN%60))
  printf 'BUNKERGAME AAA OVERNIGHT WATCHDOG\n'
  printf '=================================\n'
  printf 'Current time:       %s\n' "$(date '+%Y-%m-%d %H:%M:%S')"
  printf 'Next check in:      %02d:%02d\n' "$MM" "$SS"
  PID=$(cat artifacts/overnight_aaa_watchdog.pid 2>/dev/null)
  if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then printf 'Watchdog:           RUNNING (PID %s)\n' "$PID"; else printf 'Watchdog:           NOT RUNNING\n'; fi
  if pgrep -f 'opencode serve' >/dev/null; then printf 'OpenCode server:    UP\n'; else printf 'OpenCode server:    DOWN\n'; fi
  if pgrep -f 'rojo serve' >/dev/null; then printf 'Rojo:               UP\n'; else printf 'Rojo:               DOWN\n'; fi
  if pgrep -f 'RobloxStudio' >/dev/null; then printf 'Roblox Studio:      UP\n'; else printf 'Roblox Studio:      DOWN\n'; fi
  printf '\n--- WATCHDOG / RECOVERY OUTPUT ---\n'
  tail -35 "$LOG" 2>/dev/null
  printf '\n--- PROCESS OUTPUT ---\n'
  tail -15 "$NOHUP" 2>/dev/null
  printf '\nRefreshing every second. Ctrl+C closes this dashboard only.\n'
  sleep 1
done
