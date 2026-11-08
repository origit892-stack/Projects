#!/bin/zsh
echo '=== Pre: Roblox processes ==='
for pid in $(ps aux | grep -i robloxstudio | grep -v grep | awk '{print $2}'); do
  cmd=$(ps -p "$pid" -o command=)
  task=$(echo "$cmd" | grep -oE '\-task [^ ]+' | head -1)
  inst=$(echo "$cmd" | grep -oE '\-instanceId [^ ]+' | head -1)
  echo "PID $pid | $task | $inst"
done

echo '=== Activate RobloxStudio ==='
osascript -e 'tell application "System Events" to tell process "RobloxStudio" to set frontmost to true' 2>&1
sleep 1.5
echo 'Frontmost: '
osascript -e 'tell application "System Events" to get name of first process whose frontmost is true' 2>&1

echo '=== Sending F5 (key code 96) = Play (client) ==='
osascript -e 'tell application "System Events" to key code 96' 2>&1
echo "osascript exit: $?"

sleep 6
echo '=== Post: Roblox window title ==='
osascript -e 'tell app "System Events" to get the title of every window of (processes whose background only is false)' 2>&1 | tr ',' '\n' | grep -i 'roblox' || echo '(none)'
echo '=== Post: Roblox processes ==='
for pid in $(ps aux | grep -i robloxstudio | grep -v grep | awk '{print $2}'); do
  cmd=$(ps -p "$pid" -o command=)
  task=$(echo "$cmd" | grep -oE '\-task [^ ]+' | head -1)
  players=$(echo "$cmd" | grep -oE '\-numTestServerPlayersUponStartup [^ ]+' | head -1)
  inst=$(echo "$cmd" | grep -oE '\-instanceId [^ ]+' | head -1)
  echo "PID $pid | $task | $players | $inst"
done