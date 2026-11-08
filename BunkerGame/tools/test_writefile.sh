#!/bin/zsh
cd /Users/Ori/Documents/Projects/BunkerGame
MARKER="argon_probe_$(date +%s)"
echo "MARKER=$MARKER"

echo '=== Running writefile probe via argon exec ==='
argon exec "local ok, err = pcall(writefile, '$MARKER.txt', 'hello'); local ok2, err2 = pcall(writefile, '/tmp/$MARKER.txt', 'hello'); return tostring(ok) .. '|' .. tostring(err) .. '||' .. tostring(ok2) .. '|' .. tostring(err2)" 2>&1 | head

sleep 1
echo '=== Search for marker file everywhere ==='
find '/Users/Ori/Library/Application Support/Roblox' -name "$MARKER.txt" 2>/dev/null
find /tmp -name "$MARKER.txt" 2>/dev/null
find /Users/Ori/Documents/Projects/BunkerGame -name "$MARKER.txt" 2>/dev/null
echo '=== Recently modified files in Roblox studio data (last 3 min) ==='
find '/Users/Ori/Library/Application Support/Roblox' -type f -mmin -3 2>/dev/null | head -20
echo '=== studio dir contents ==='
ls -la '/Users/Ori/Library/Application Support/Roblox/studio/' 2>&1 | head