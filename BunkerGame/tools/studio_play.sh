#!/bin/zsh
# Usage: studio_play.sh <stop|play|run|start>
MODE="$1"

echo '=== Activating RobloxStudio process ==='
osascript -e 'tell application "System Events" to tell process "RobloxStudio" to set frontmost to true' 2>&1
sleep 1.5

echo '=== Current frontmost app ==='
osascript -e 'tell application "System Events" to get name of first process whose frontmost is true' 2>&1

echo '=== Sending mode: '$MODE' ==='
cd /Users/Ori/Documents/Projects/BunkerGame
argon debug "$MODE" 2>&1
echo "argon exit: $?"

sleep 3
echo '=== Window titles after ==='
osascript -e 'tell app "System Events" to get the title of every window of (processes whose background only is false)' 2>&1 | tr ',' '\n' | grep -i 'roblox\|studio' || echo '(no roblox window title found)'
echo '=== Roblox processes ==='
for pid in $(ps aux | grep -i robloxstudio | grep -v grep | awk '{print $2}'); do
  cmd=$(ps -p "$pid" -o command=)
  task=$(echo "$cmd" | grep -oE '\-task [^ ]+' | head -1)
  players=$(echo "$cmd" | grep -oE '\-numTestServerPlayersUponStartup [^ ]+' | head -1)
  inst=$(echo "$cmd" | grep -oE '\-instanceId [^ ]+' | head -1)
  echo "PID $pid | $task | $players | $inst"
done