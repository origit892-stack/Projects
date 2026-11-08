#!/bin/bash
set -e
BRIDGE_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$BRIDGE_DIR/assistant_relay.pid"
if [ ! -f "$PID_FILE" ]; then
  echo "No PID file, relay not running?"
  PIDS=$(pgrep -f "tools/assistant_bloxforge_bridge/assistant_relay.py" || true)
  if [ -n "$PIDS" ]; then
    echo "Found PIDs $PIDS, killing"
    kill $PIDS || true
    sleep 1
    PIDS2=$(pgrep -f "tools/assistant_bloxforge_bridge/assistant_relay.py" || true)
    if [ -n "$PIDS2" ]; then kill -9 $PIDS2 || true; fi
    rm -f "$PID_FILE"
  fi
  exit 0
fi
PID=$(cat "$PID_FILE")
echo "Stopping relay PID $PID"
if kill -0 "$PID" 2>/dev/null; then
  kill "$PID"
  for i in 1 2 3 4 5; do
    if ! kill -0 "$PID" 2>/dev/null; then break; fi
    sleep 1
  done
  if kill -0 "$PID" 2>/dev/null; then
    echo "Force killing $PID"
    kill -9 "$PID" || true
  fi
fi
rm -f "$PID_FILE"
echo "Relay stopped"
