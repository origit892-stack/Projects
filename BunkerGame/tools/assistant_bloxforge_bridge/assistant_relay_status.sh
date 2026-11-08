#!/bin/bash
BRIDGE_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$BRIDGE_DIR/assistant_relay.pid"
PORT_FILE="$BRIDGE_DIR/relay_port.txt"
LOG_FILE="$BRIDGE_DIR/logs/assistant_relay.log"
echo "=== Assistant Relay Status ==="
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
  PIDS=$(pgrep -f "tools/assistant_bloxforge_bridge/assistant_relay.py" || true)
  if [ -n "$PIDS" ]; then echo "But found running PIDs: $PIDS"; else echo "Relay not running"; fi
fi
if [ -f "$PORT_FILE" ]; then echo "Port: $(cat "$PORT_FILE")"; else echo "No port file"; fi
echo "--- Log tail (last 20) ---"
if [ -f "$LOG_FILE" ]; then tail -n 20 "$LOG_FILE"; else echo "No log"; fi
echo "--- Listening sockets ---"
if [ -f "$PORT_FILE" ]; then
  PORT=$(cat "$PORT_FILE")
  lsof -nP -iTCP:$PORT -sTCP:LISTEN 2>/dev/null || echo "No listen on $PORT"
fi
echo "--- Health check (no credential) ---"
if [ -f "$PORT_FILE" ]; then
  PORT=$(cat "$PORT_FILE")
  curl -s http://127.0.0.1:$PORT/health 2>&1 | head -c 300; echo
fi
