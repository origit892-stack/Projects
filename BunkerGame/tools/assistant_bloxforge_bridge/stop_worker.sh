#!/bin/bash
set -e
BRIDGE_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$BRIDGE_DIR/worker.pid"
if [ ! -f "$PID_FILE" ]; then
  echo "No PID file, worker not running?"
  # Try to find by process name
  PIDS=$(pgrep -f "tools/assistant_bloxforge_bridge/worker.py" || true)
  if [ -n "$PIDS" ]; then
    echo "Found worker PIDs $PIDS, killing"
    kill $PIDS || true
    sleep 1
    # Force kill if still alive
    PIDS2=$(pgrep -f "tools/assistant_bloxforge_bridge/worker.py" || true)
    if [ -n "$PIDS2" ]; then kill -9 $PIDS2 || true; fi
    rm -f "$PID_FILE"
    exit 0
  fi
  exit 0
fi
PID=$(cat "$PID_FILE")
echo "Stopping worker PID $PID"
if kill -0 "$PID" 2>/dev/null; then
  kill "$PID"
  # Wait up to 5s
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
# Also clean up claim files if any stale?
echo "Worker stopped"
