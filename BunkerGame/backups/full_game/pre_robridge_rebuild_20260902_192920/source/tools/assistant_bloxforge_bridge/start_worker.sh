#!/bin/bash
set -e
BRIDGE_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKER_PY="$BRIDGE_DIR/worker.py"
LOG_FILE="$BRIDGE_DIR/logs/worker.log"
PID_FILE="$BRIDGE_DIR/worker.pid"

if [ -f "$PID_FILE" ]; then
  OLD_PID=$(cat "$PID_FILE")
  if kill -0 "$OLD_PID" 2>/dev/null; then
    echo "Worker already running with PID $OLD_PID"
    exit 1
  else
    echo "Removing stale PID file"
    rm -f "$PID_FILE"
  fi
fi

echo "Starting BloxForge Worker v1..."
# Ensure logs dir exists
mkdir -p "$BRIDGE_DIR/logs"
# Start worker in background, detached
nohup python3 "$WORKER_PY" >> "$LOG_FILE" 2>&1 &
PID=$!
echo $PID > "$PID_FILE"
echo "Worker started PID=$PID LOG=$LOG_FILE"
# Give it a moment to start
sleep 1
if kill -0 "$PID" 2>/dev/null; then
  echo "Worker is running"
  exit 0
else
  echo "Worker failed to start, check $LOG_FILE"
  cat "$LOG_FILE" | tail -n 20
  exit 1
fi
