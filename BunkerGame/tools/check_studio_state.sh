#!/bin/zsh
echo '=== WINDOW TITLES ==='
osascript -e 'tell app "System Events" to get the title of every window of (processes whose background only is false)' 2>&1
echo
echo '=== ROBLOX PROCESSES ==='
for pid in $(ps aux | grep -i robloxstudio | grep -v grep | awk '{print $2}'); do
  cmd=$(ps -p "$pid" -o command=)
  task=$(echo "$cmd" | grep -oE '\-task [^ ]+' | head -1)
  players=$(echo "$cmd" | grep -oE '\-numTestServerPlayersUponStartup [^ ]+' | head -1)
  inst=$(echo "$cmd" | grep -oE '\-instanceId [^ ]+' | head -1)
  echo "PID $pid | $task | $players | $inst"
done