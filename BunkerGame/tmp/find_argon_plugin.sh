#!/bin/zsh
echo '=== argon under Roblox support ==='
find "/Users/Ori/Library/Application Support/Roblox" -iname '*argon*' 2>/dev/null | head -20
echo '=== studio dir ==='
ls "/Users/Ori/Library/Application Support/Roblox/studio/" 2>/dev/null | head
echo '=== plugins dir ==='
ls "/Users/Ori/Library/Application Support/Roblox/studio/plugins/" 2>/dev/null | head -30