#!/bin/zsh
echo "===ROBLOXSTUDIO SUPPORT DIR==="
ls -la "$HOME/Library/Application Support/Roblox/RobloxStudio/" 2>/dev/null | head -20
echo "===FIND PLUGIN DIRS==="
find "$HOME/Library/Application Support/Roblox/RobloxStudio" -maxdepth 2 -type d 2>/dev/null | head -20
echo "===FIND rojo/argon plugin files==="
find "$HOME/Library/Application Support/Roblox" -iname "*.rbmx" 2>/dev/null | head -20
echo "===PLACE NAME IN LOG==="
grep -iE "PlaceName|Opened place|place:" "/Users/Ori/Library/Logs/Roblox/0.740.19.7400931_20260926T070125Z_Studio_cb069_last.log" 2>/dev/null | tail -5
echo "===ANY SUCCESSFUL CONNECT (non-error ws lines)==="
grep -E "ws: [0-9]+ url: http://localhost:13469" "/Users/Ori/Library/Logs/Roblox/0.740.19.7400931_20260926T070125Z_Studio_cb069_last.log" 2>/dev/null | grep -v "error" | tail -5
echo "===DONE==="