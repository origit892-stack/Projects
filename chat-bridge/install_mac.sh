#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
BASE="$HOME/.chat-bridge"
VENV="$BASE/venv"
CONFIG="$BASE/config.json"

mkdir -p "$BASE"
if [ ! -x "$VENV/bin/python" ]; then
  python3 -m venv "$VENV"
fi
"$VENV/bin/python" -m pip install --upgrade pip
"$VENV/bin/python" -m pip install -r "$ROOT/host/requirements.txt"

if [ ! -f "$CONFIG" ]; then
  "$VENV/bin/python" - <<'PY'
import json, secrets, os
from pathlib import Path
base = Path.home() / ".chat-bridge"
config = {
    "token": secrets.token_urlsafe(36),
    "db_path": str(base / "chat-bridge.sqlite3")
}
path = base / "config.json"
path.write_text(json.dumps(config, indent=2), encoding="utf-8")
os.chmod(path, 0o600)
PY
fi
chmod 600 "$CONFIG"
TOKEN="$("$VENV/bin/python" -c 'import json,sys; print(json.load(open(sys.argv[1]))["token"])' "$CONFIG")"

cat <<EOF2

Chat Bridge setup completed.

1) Copy this token into Chrome > Chat Bridge > Settings:
$TOKEN

2) Load the extension:
   - Open chrome://extensions
   - Enable Developer mode
   - Click Load unpacked
   - Select: $ROOT/extension

3) Start the local service by double-clicking:
   $ROOT/start.command
   Keep its Terminal window open while using Chat Bridge.

4) Configure Hermes and OpenCode using the examples in:
   $ROOT/configs/

Database: $BASE/chat-bridge.sqlite3
Project:  $ROOT

The token is stored in $CONFIG with owner-only file permissions.
EOF2
