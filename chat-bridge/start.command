#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
PY="$HOME/.chat-bridge/venv/bin/python"
if [ ! -x "$PY" ]; then
  echo "Run install_mac.sh first."
  read -r -p "Press Enter to close..."
  exit 1
fi
export PYTHONPATH="$ROOT/host${PYTHONPATH:+:$PYTHONPATH}"
exec "$PY" "$ROOT/host/bridge_daemon.py"
