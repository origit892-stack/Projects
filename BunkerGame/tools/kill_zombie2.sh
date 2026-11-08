#!/bin/zsh
sleep 3
echo '=== 38370 still alive? ==='
if ps -p 38370 > /dev/null 2>&1; then
  echo 'STILL ALIVE - escalating to SIGKILL'
  kill -9 38370 2>&1
  echo "kill -9 exit: $?"
  sleep 2
else
  echo '38370 exited cleanly'
fi
echo '=== Final Roblox process check ==='
ps aux | grep -i roblox | grep -v grep | awk '{print $2, $11, $12, $13}'
echo '=== done ==='