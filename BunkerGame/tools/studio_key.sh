#!/bin/zsh
# Send a specific key code to RobloxStudio, optionally with shift
# Usage: studio_key.sh <keycode> [shift]
KEYCODE="$1"
SHIFT="$2"

echo '=== Activate RobloxStudio ==='
osascript -e 'tell application "System Events" to tell process "RobloxStudio" to set frontmost to true' 2>&1
sleep 1.5

echo '=== Frontmost app ==='
osascript -e 'tell application "System Events" to get name of first process whose frontmost is true' 2>&1

if [ "$SHIFT" = "shift" ]; then
  echo '=== Sending key code '$KEYCODE' with shift ==='
  osascript -e 'tell application "System Events" to keystroke ("" as text) ' 2>/dev/null
  osascript -e 'tell application "System Events" to key code '$KEYCODE' using shift down' 2>&1
else
  echo '=== Sending key code '$KEYCODE' ==='
  osascript -e 'tell application "System Events" to key code '$KEYCODE'' 2>&1
fi
echo "osascript exit: $?"

sleep 3
echo '=== Roblox window title ==='
osascript -e 'tell app "System Events" to get the title of every window of (processes whose background only is false)' 2>&1 | tr ',' '\n' | grep -i 'roblox' || echo '(none)'
echo '=== Roblox processes ==='
for pid in $(ps aux | grep -i robloxstudio | grep -v grep | awk '{print $2}'); do
  cmd=$(ps -p "$pid" -o command=)
  task=$(echo "$cmd" | grep -oE '\-task [^ ]+' | head -1)
  inst=$(echo "$cmd" | grep -oE '\-instanceId [^ ]+' | head -1)
  echo "PID $pid | $task | $inst"
done