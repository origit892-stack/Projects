#!/bin/zsh
echo '=== All windows with process names (Roblox-related) ==='
osascript <<'EOF' 2>&1
tell application "System Events"
  repeat with p in (every process whose name contains "Roblox" or name contains "Studio")
    set pname to name of p
    try
      repeat with w in (every window of p)
        set wtitle to name of w
        set wpos to position of w
        set wsize to size of w
        log "PROC: " & pname & " | TITLE: " & wtitle & " | POS: " & (item 1 of wpos) & "," & (item 2 of wpos) & " | SIZE: " & (item 1 of wsize) & "x" & (item 2 of wsize)
      end repeat
    on error
      log "PROC: " & pname & " | (no windows)"
    end try
  end repeat
end tell
EOF
echo '=== Roblox processes (full) ==='
ps aux | grep -i roblox | grep -v grep | awk '{print $2, $11, $12, $13, $14, $15, $16}'