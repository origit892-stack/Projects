#!/bin/zsh
echo '=== RobloxStudio menu bar ==='
osascript <<'EOF' 2>&1
tell application "System Events"
  tell process "RobloxStudio"
    set frontmost to true
    delay 0.5
    try
      set mb to menu bar 1
      repeat with mbi in (every menu bar item of mb)
        set mname to name of mbi
        log "MENU: " & mname
        try
          repeat with mi in (every menu item of menu 1 of mbi)
            set mititle to name of mi
            log "   ITEM: " & mititle
          end repeat
        end try
      end repeat
    on error errMsg
      log "ERROR: " & errMsg
    end try
  end tell
end tell
EOF