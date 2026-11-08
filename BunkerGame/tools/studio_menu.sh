#!/bin/zsh
# Usage: studio_menu.sh <MenuName> <ItemName>
MENU="$1"
ITEM="$2"

echo '=== Clicking Test > '$ITEM' ==='
osascript <<EOF 2>&1
tell application "System Events"
  tell process "RobloxStudio"
    set frontmost to true
    delay 0.5
    click menu item "$ITEM" of menu 1 of menu bar item "$MENU" of menu bar 1
  end tell
end tell
EOF
echo "osascript exit: $?"

sleep 4
echo '=== Window title ==='
osascript -e 'tell app "System Events" to get the title of every window of (processes whose background only is false)' 2>&1 | tr ',' '\n' | grep -i 'roblox' || echo '(none)'
echo '=== Roblox processes ==='
for pid in $(ps aux | grep -i robloxstudio | grep -v grep | awk '{print $2}'); do
  cmd=$(ps -p "$pid" -o command=)
  task=$(echo "$cmd" | grep -oE '\-task [^ ]+' | head -1)
  inst=$(echo "$cmd" | grep -oE '\-instanceId [^ ]+' | head -1)
  echo "PID $pid | $task | $inst"
done