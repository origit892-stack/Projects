#!/bin/zsh
echo '=== Most recent Roblox logs ==='
ls -lat /Users/Ori/Library/Logs/Roblox/*.log 2>/dev/null | head -4
NEWEST=$(ls -t /Users/Ori/Library/Logs/Roblox/*.log 2>/dev/null | head -1)
echo "NEWEST: $NEWEST"
echo '=== Last 20 lines ==='
tail -20 "$NEWEST" 2>&1
echo '=== 38370 CPU now ==='
ps -p 38370 -o pid,stat,%cpu,etime 2>&1