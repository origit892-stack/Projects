#!/bin/zsh
echo '=== Activate RobloxStudio ==='
osascript -e 'tell application "System Events" to tell process "RobloxStudio" to set frontmost to true' 2>&1
sleep 3
echo '=== Frontmost app ==='
osascript -e 'tell application "System Events" to get name of first process whose frontmost is true' 2>&1
echo '=== Window count + names ==='
osascript <<'EOF' 2>&1
tell application "System Events"
  tell process "RobloxStudio"
    set wc to count of windows
    log "window count: " & wc
    repeat with i from 1 to wc
      set w to window i
      log "  win" & i & " name=[" & (name of w) & "]"
    end repeat
  end tell
end tell
EOF
echo '=== 38370 state ==='
ps -p 38370 -o pid,stat,%cpu,etime 2>&1