#!/bin/bash
set -e
BRIDGE_DIR="$(cd "$(dirname "$0")" && pwd)"
RELAY_PY="$BRIDGE_DIR/assistant_relay.py"
LOG_FILE="$BRIDGE_DIR/logs/assistant_relay.log"
PID_FILE="$BRIDGE_DIR/assistant_relay.pid"
PORT_FILE="$BRIDGE_DIR/relay_port.txt"

if [ -f "$PID_FILE" ]; then
  OLD_PID=$(cat "$PID_FILE")
  if kill -0 "$OLD_PID" 2>/dev/null; then
    echo "Relay already running PID $OLD_PID"
    exit 1
  else
    echo "Removing stale PID file"
    rm -f "$PID_FILE"
  fi
fi

echo "Starting Assistant Local Relay..."
mkdir -p "$BRIDGE_DIR/logs"
nohup python3 "$RELAY_PY" >> "$LOG_FILE" 2>&1 &
PID=$!
echo $PID > "$PID_FILE"
echo "Relay started PID=$PID LOG=$LOG_FILE"
sleep 1
if kill -0 "$PID" 2>/dev/null; then
  PORT=$(cat "$PORT_FILE" 2>/dev/null || echo "62413")
  echo "Relay is running on 127.0.0.1:$PORT"
  # Verify loopback only
  BOUND=$(lsof -nP -iTCP:$PORT -sTCP:LISTEN 2>/dev/null | grep LISTEN | head -n 1 || echo "not found")
  echo "Bound: $BOUND"
  if echo "$BOUND" | grep -q "127.0.0.1:$PORT"; then
    echo "Loopback only: PASS"
  else
    echo "Loopback check: see above"
  fi
  exit 0
else
  echo "Relay failed to start, check $LOG_FILE"
  cat "$LOG_FILE" | tail -n 20
  exit 1
fi
