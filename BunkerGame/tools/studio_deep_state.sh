#!/bin/zsh
echo '=== RobloxStudio windows (incl. sheets/dialogs) ==='
osascript <<'EOF' 2>&1
tell application "System Events"
  tell process "RobloxStudio"
    set wc to count of windows
    log "window count: " & wc
    repeat with i from 1 to wc
      set w to window i
      log "  win" & i & " name=[" & (name of w) & "] subrole=[" & (subrole of w) & "]"
    end repeat
  end tell
end tell
EOF
echo '=== Process 38370 state ==='
ps -p 38370 -o pid,stat,etime,%cpu,%mem 2>&1
echo '=== argon sessions ==='
cat ~/.argon/sessions.toml 2>&1
echo '=== argon exec connectivity test ==='
cd /Users/Ori/Documents/Projects/BunkerGame
argon exec 'return 1' 2>&1 | head -3