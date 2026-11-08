#!/bin/bash
BRIDGE_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$BRIDGE_DIR/worker.pid"
LOG_FILE="$BRIDGE_DIR/logs/worker.log"
echo "=== BloxForge Worker v1 Status ==="
if [ -f "$PID_FILE" ]; then
  PID=$(cat "$PID_FILE")
  if kill -0 "$PID" 2>/dev/null; then
    echo "PID: $PID (running)"
    ps -p "$PID" -o pid,ppid,etime,command | tail -n 5
  else
    echo "PID file exists but process $PID not running (stale)"
  fi
else
  echo "PID file not found"
  # Check pgrep
  PIDS=$(pgrep -f "tools/assistant_bloxforge_bridge/worker.py" || true)
  if [ -n "$PIDS" ]; then
    echo "But found running PIDs: $PIDS"
  else
    echo "Worker not running"
  fi
fi
echo "--- Log tail (last 20) ---"
if [ -f "$LOG_FILE" ]; then tail -n 20 "$LOG_FILE"; else echo "No log"; fi
echo "--- Queue ---"
echo "Requests: $(ls -1 "$BRIDGE_DIR/requests"/*.json 2>/dev/null | wc -l) files"
echo "State: $(ls -1 "$BRIDGE_DIR/state"/*.json 2>/dev/null | wc -l) files"
echo "Responses: $(ls -1 "$BRIDGE_DIR/responses"/*.json 2>/dev/null | wc -l) files"
echo "--- BloxForge Health ---"
curl -s http://127.0.0.1:58741/health | head -c 200; echo
