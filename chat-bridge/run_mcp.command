#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
PY="$HOME/.chat-bridge/venv/bin/python"
if [ ! -x "$PY" ]; then
  echo "Run install_mac.sh first." >&2
  exit 1
fi
export PYTHONPATH="$ROOT/host${PYTHONPATH:+:$PYTHONPATH}"
exec "$PY" "$ROOT/host/mcp_server.py"
