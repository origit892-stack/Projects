#!/bin/zsh
echo '=== Local place files (.rbxlx/.rbxl) in project ==='
find /Users/Ori/Documents/Projects/BunkerGame -maxdepth 2 -iname '*.rbxlx' -o -maxdepth 2 -iname '*.rbxl' 2>/dev/null | head
echo '=== argon studio help ==='
cd /Users/Ori/Documents/Projects/BunkerGame
argon studio --help 2>&1 | head -25
echo '=== argon serve process still alive? ==='
ps -p 35411 -o pid,stat,command= 2>&1 | head -c 200
echo
echo '=== hung 38370 ==='
ps -p 38370 -o pid,stat,%cpu,etime 2>&1