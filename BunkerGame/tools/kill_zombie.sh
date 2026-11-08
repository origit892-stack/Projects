#!/bin/zsh
echo '=== Before: Roblox processes ==='
ps aux | grep -i roblox | grep -v grep | awk '{print $2, $11, $12, $13}'
echo '=== SIGTERM 38370 and 38372 ==='
kill -TERM 38370 2>&1; echo "term 38370 exit: $?"
kill -TERM 38372 2>&1; echo "term 38372 exit: $?"
sleep 4
echo '=== After SIGTERM: still alive? ==='
ps -p 38370 -o pid,stat 2>&1
ps -p 38372 -o pid,stat 2>&1